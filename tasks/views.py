import json
import datetime
from tasks.models import Task, Project
from utils.time import get_current_time_ts
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from utils.response import response_success,response_fail
from django.views.decorators.http import require_http_methods

def hello(request):
    data = {
        "user": "chris",
        "project": "COMPSCI5012",
        "status": "Backend ready"
    }
    return response_success(
        data=data,
    )

@csrf_exempt
@require_http_methods(["POST"])
def add_task(request):
    try:
        body = json.loads(request.body or "{}")
        uid = body.get("uid", "")
        title = str(body.get("title", "")).strip()
        description = str(body.get("description", "")).strip()
        priority = int(body.get("priority", Task.Priority.MEDIUM))
        project_id = body.get("project_id", None)

        start_time_ts = body.get("start_time_ts")
        end_time_ts = body.get("end_time_ts")

        if not uid:
            return response_fail("uid is required")

        if not title:
            return response_fail("Title is required")

        if start_time_ts in ["", None]:
            return response_fail("start_time_ts is required")

        if end_time_ts in ["", None]:
            return response_fail("end_time_ts is required")

        try:
            uid = int(uid)
            start_time_ts = int(start_time_ts)
            end_time_ts = int(end_time_ts)
        except (TypeError, ValueError):
            return response_fail("uid/start_time_ts/end_time_ts format is invalid")

        if project_id not in ["", None]:
            try:
                project_id = int(project_id)
            except (TypeError, ValueError):
                return response_fail("project_id format is invalid")
        else:
            project_id = None

        if end_time_ts <= start_time_ts:
            return response_fail("end_time_ts must be greater than start_time_ts")

        if priority not in [
            Task.Priority.LOW,
            Task.Priority.MEDIUM,
            Task.Priority.HIGH
        ]:
            return response_fail("priority is invalid")

        task = Task.objects.create(
            uid=uid,
            title=title,
            description=description,
            status=Task.Status.TODO,
            priority=priority,
            start_time_ts=start_time_ts,
            end_time_ts=end_time_ts,
            completed_at_ts=None,
            project_id=project_id,
        )

        return response_success({
            "id": task.id,
            "title": task.title,
            "msg": "Created successfully"
        })

    except json.JSONDecodeError:
        return response_fail("Invalid JSON body")
    except Exception as e:
        return response_fail(str(e))
  


@csrf_exempt
@require_http_methods(["GET"])
def get_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, is_deleted=0)
    except Task.DoesNotExist as e:
        return response_fail(str(e))

    return response_success({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "uid": task.uid,
        "status": task.status,
        "priority": task.priority,
        "start_time_ts": task.start_time_ts,
        "end_time_ts": task.end_time_ts,
        "completed_at_ts": task.completed_at_ts,
        "project_id": task.project_id,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "is_deleted": task.is_deleted,
    })


@csrf_exempt
@require_http_methods(["PUT"])
def put_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, is_deleted=0)
    except Task.DoesNotExist:
        return response_fail("Task not found")

    try:
        body = json.loads(request.body)

        if "title" in body:
            title = body.get("title")
            if title is not None:
                title = str(title).strip()
                if not title:
                    return response_fail("Title is required")
                task.title = title
        if "description" in body:
            task.description = body.get("description")
        if "status" in body:
            task.status = body.get("status")
        if "priority" in body:
            task.priority = body.get("priority")
        if "start_time_ts" in body:
            task.start_time_ts = body.get("start_time_ts")
        if "end_time_ts" in body:
            task.end_time_ts = body.get("end_time_ts")
        if "completed_at_ts" in body:
            task.completed_at_ts = body.get("completed_at_ts")
        if "project_id" in body:
            task.project_id = body.get("project_id")
        task.save()

        return response_success({
            "id": task.id,
            "title": task.title,
            "msg": "Updated successfully"
        })

    except json.JSONDecodeError:
        return response_fail("Invalid JSON")
    except Exception as e:
        return response_fail(str(e))


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist as e:
        return response_fail(str(e))

    task.is_deleted = 1
    task.save()
    return response_success({"deleted": True})


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def task_detail(request, task_id):
    if request.method == "GET":
        return get_task(request, task_id)
    elif request.method == "PUT":
        return put_task(request, task_id)
    elif request.method == "DELETE":
        return delete_task(request, task_id)


@csrf_exempt
@require_http_methods(["GET"])
def task_list(request):
    filter_date = request.GET.get('date')
    tasks = Task.objects.all().order_by('-created_at')
   
    if filter_date == 'today':
        today = datetime.date.today()
        tasks = tasks.filter(due_date__date=today)
    elif filter_date == 'completed':
        tasks = tasks.filter(status=3)
    
    data = []
    for task in tasks:
        data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'created_at': task.created_at.isoformat(),
            'owner': task.owner.username,
            'executor_id': task.executor_id,
        })
    return response_success(data)

