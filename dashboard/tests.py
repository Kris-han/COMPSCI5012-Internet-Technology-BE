import json
import time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from tasks.models import Task, Project


class DashboardListTest(TestCase):
    """Test GET /dashboard/dashboard_list/ — monthly status counts"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.uid = str(self.user.id)

    def _make_task(self, status):
        now = int(time.time())
        return Task.objects.create(
            uid=self.uid,
            title=f"Task status {status}",
            owner=self.user,
            status=status,
            start_time_ts=now,
            end_time_ts=now + 3600,
        )

    def test_dashboard_list_missing_uid_returns_error(self):
        """No uid parameter → success=False"""
        response = self.client.get('/dashboard/dashboard_list/')
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_dashboard_list_correct_counts(self):
        """Creates 1 task per status, asserts each count == 1"""
        self._make_task(Task.Status.TODO)
        self._make_task(Task.Status.IN_PROGRESS)
        self._make_task(Task.Status.COMPLETED)
        self._make_task(Task.Status.POSTPONED)

        response = self.client.get(f'/dashboard/dashboard_list/?uid={self.uid}')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['todo_data'],   1)
        self.assertEqual(data['data']['doing_data'],  1)
        self.assertEqual(data['data']['finish_data'], 1)
        self.assertEqual(data['data']['delay_data'],  1)

    def test_dashboard_list_empty_returns_empty_dict(self):
        """No tasks for this user → empty data dict"""
        response = self.client.get(f'/dashboard/dashboard_list/?uid={self.uid}')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data'], {})


class DueListTest(TestCase):
    """Test GET /dashboard/due_list/ — urgency time-window counts"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.uid = str(self.user.id)

    def _make_task_due_in(self, seconds_from_now):
        now = int(time.time())
        Task.objects.create(
            uid=self.uid,
            title=f"Due in {seconds_from_now}s",
            owner=self.user,
            start_time_ts=now,
            end_time_ts=now + seconds_from_now,
        )

    def test_due_list_missing_uid_returns_error(self):
        """No uid parameter → success=False"""
        response = self.client.get('/dashboard/due_list/')
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_due_list_task_due_within_24h(self):
        """Task due in 1 hour appears in 24_hours, 7_days, 14_days, month"""
        self._make_task_due_in(3600)  # 1 hour
        response = self.client.get(f'/dashboard/due_list/?uid={self.uid}')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['24_hours'], 1)
        self.assertEqual(data['data']['7_days'],   1)
        self.assertEqual(data['data']['14_days'],  1)
        self.assertEqual(data['data']['month'],    1)

    def test_due_list_task_due_in_3_days(self):
        """Task due in 3 days: not in 24h, but in 7d/14d/month"""
        self._make_task_due_in(3 * 24 * 3600)
        response = self.client.get(f'/dashboard/due_list/?uid={self.uid}')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['24_hours'], 0)
        self.assertEqual(data['data']['7_days'],   1)
        self.assertEqual(data['data']['14_days'],  1)

    def test_due_list_task_due_in_10_days(self):
        """Task due in 10 days: not in 24h or 7d, but in 14d/month"""
        self._make_task_due_in(10 * 24 * 3600)
        response = self.client.get(f'/dashboard/due_list/?uid={self.uid}')
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['24_hours'], 0)
        self.assertEqual(data['data']['7_days'],   0)
        self.assertEqual(data['data']['14_days'],  1)


class DashboardTaskListTest(TestCase):
    """Test POST /dashboard/task_list/ — paginated upcoming tasks"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.uid = str(self.user.id)

    def _make_tasks(self, count):
        now = int(time.time())
        for i in range(count):
            Task.objects.create(
                uid=self.uid,
                title=f"Task {i+1}",
                owner=self.user,
                start_time_ts=now,
                end_time_ts=now + (i + 1) * 3600,
            )

    def test_task_list_missing_uid_returns_error(self):
        """No uid → success=False"""
        response = self.client.post(
            '/dashboard/task_list/',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_task_list_returns_correct_page(self):
        """10 tasks, page_size=3, page 1 → 3 items, has_next=True"""
        self._make_tasks(10)
        payload = {"uid": self.uid, "page_size": 3, "page_number": 1}
        response = self.client.post(
            '/dashboard/task_list/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['list']), 3)
        self.assertEqual(data['data']['total'], 10)
        self.assertTrue(data['data']['has_next'])

    def test_task_list_last_page_has_next_false(self):
        """10 tasks, page_size=3, page 4 → 1 item, has_next=False"""
        self._make_tasks(10)
        payload = {"uid": self.uid, "page_size": 3, "page_number": 4}
        response = self.client.post(
            '/dashboard/task_list/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['list']), 1)
        self.assertFalse(data['data']['has_next'])

    def test_task_list_default_page_size(self):
        """5 tasks, no page params → returns all 5, has_next=False"""
        self._make_tasks(5)
        payload = {"uid": self.uid}
        response = self.client.post(
            '/dashboard/task_list/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['list']), 5)
        self.assertFalse(data['data']['has_next'])
