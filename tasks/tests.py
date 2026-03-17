import json
import time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from tasks.models import Task, Project


# ─────────────────────────────────────────────
#  PART 1 — Model Tests
# ─────────────────────────────────────────────

class ProjectModelTest(TestCase):
    """Test the Project model"""

    def test_project_creation(self):
        """Project can be created and fields are saved correctly"""
        project = Project.objects.create(name="Test Project")
        self.assertEqual(project.name, "Test Project")
        self.assertIsNotNone(project.create_time)

    def test_project_str(self):
        """__str__ returns the project name"""
        project = Project.objects.create(name="My Project")
        self.assertEqual(str(project), "My Project")


class TaskModelTest(TestCase):
    """Test the Task model"""

    def setUp(self):
        # Create a test user (needed because Task has a ForeignKey to User)
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def _make_task(self, **kwargs):
        """Helper: create a minimal valid Task"""
        defaults = {
            'uid': str(self.user.id),
            'title': 'Default Task',
            'owner': self.user,
            'start_time_ts': int(time.time()),
            'end_time_ts': int(time.time()) + 3600,
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    def test_task_default_status_is_todo(self):
        """New task's status defaults to TODO (1)"""
        task = self._make_task(title="Status Test")
        self.assertEqual(task.status, Task.Status.TODO)

    def test_task_default_priority_is_medium(self):
        """New task's priority defaults to MEDIUM (2)"""
        task = self._make_task(title="Priority Test")
        self.assertEqual(task.priority, Task.Priority.MEDIUM)

    def test_task_str_returns_title(self):
        """__str__ returns the task title"""
        task = self._make_task(title="My Task Title")
        self.assertEqual(str(task), "My Task Title")

    def test_task_description_optional(self):
        """Task can be created without a description (defaults to None)"""
        task = self._make_task(title="No Desc Task")
        self.assertIsNone(task.description)

    def test_task_owner_relationship(self):
        """Task owner is correctly linked to the User"""
        task = self._make_task(title="Owner Test")
        self.assertEqual(task.owner.username, 'testuser')

    def test_task_with_project(self):
        """Task can be linked to a Project"""
        project = Project.objects.create(name="Test Project")
        task = self._make_task(title="Task with Project", project=project)
        self.assertEqual(task.project.name, "Test Project")

    def test_task_status_choices(self):
        """All four status values are valid"""
        for status_val in [Task.Status.TODO, Task.Status.IN_PROGRESS,
                           Task.Status.COMPLETED, Task.Status.POSTPONED]:
            task = self._make_task(title=f"Status {status_val}", status=status_val)
            self.assertEqual(task.status, status_val)

    def test_task_priority_choices(self):
        """All three priority values are valid"""
        for priority_val in [Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH]:
            task = self._make_task(title=f"Priority {priority_val}", priority=priority_val)
            self.assertEqual(task.priority, priority_val)


# ─────────────────────────────────────────────
#  PART 2 — View (API Endpoint) Tests
# ─────────────────────────────────────────────

class TaskViewTest(TestCase):
    """Test the task API endpoints"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def _make_task(self, **kwargs):
        defaults = {
            'uid': str(self.user.id),
            'title': 'Default Task',
            'owner': self.user,
            'start_time_ts': int(time.time()),
            'end_time_ts': int(time.time()) + 3600,
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    # ── Hello endpoint ──────────────────────────────────────────
    def test_hello_returns_200(self):
        """GET /task/hello/ returns HTTP 200 and success=True"""
        response = self.client.get('/task/hello/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'Backend ready')

    # ── add_task endpoint ───────────────────────────────────────
    def test_add_task_success(self):
        """POST /task/add_task with valid data creates a task"""
        payload = {
            "title": "New Task",
            "description": "A test task",
            "status": 1,
            "priority": 2,
            "due_date": "2026-12-31T23:59:59Z"
        }
        response = self.client.post(
            '/task/add_task',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('id', data['data'])
        self.assertEqual(data['data']['title'], 'New Task')

    def test_add_task_missing_title_returns_error(self):
        """POST /task/add_task without title returns success=False"""
        payload = {"description": "No title provided"}
        response = self.client.post(
            '/task/add_task',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    # ── task_detail endpoint ────────────────────────────────────
    def test_task_detail_get_returns_correct_data(self):
        """GET /task/task_detail/<id> returns the correct task"""
        task = self._make_task(title="Detail Task")
        response = self.client.get(f'/task/task_detail/{task.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['title'], 'Detail Task')

    def test_task_detail_not_found(self):
        """GET /task/task_detail/99999 returns success=False for missing task"""
        response = self.client.get('/task/task_detail/99999')
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_task_detail_put_updates_title(self):
        """PUT /task/task_detail/<id> updates the task title"""
        task = self._make_task(title="Old Title")
        payload = {"title": "Updated Title"}
        response = self.client.put(
            f'/task/task_detail/{task.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated Title")

    def test_task_detail_delete_removes_task(self):
        """DELETE /task/task_detail/<id> removes the task from database"""
        task = self._make_task(title="Delete Me")
        response = self.client.delete(f'/task/task_detail/{task.id}')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    # ── task_list endpoint ──────────────────────────────────────
    def test_task_list_returns_all_tasks(self):
        """GET /task/task_list returns all tasks"""
        self._make_task(title="Task 1")
        self._make_task(title="Task 2")
        response = self.client.get('/task/task_list')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 2)

    def test_task_list_filter_completed(self):
        """GET /task/task_list?date=completed returns only completed tasks"""
        self._make_task(title="Done Task", status=Task.Status.COMPLETED)
        self._make_task(title="Todo Task", status=Task.Status.TODO)
        response = self.client.get('/task/task_list?date=completed')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['title'], 'Done Task')
