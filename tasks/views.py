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
        body = json.loads(request.body)

        title = body.get("title", "").strip()
        description = body.get("description", "")
        status = body.get("status", 1)
        priority = body.get("priority", 2)

        project_id = body.get("project_id")
        executor_id = body.get("executor_id")

        due_date = None #todo 创建任务需要有结束时间
        if body.get("due_date"):
            try:
                due_date_str = body.get("due_date").replace("Z", "+00:00")
                due_date = datetime.datetime.fromisoformat(due_date_str)

            except ValueError:
                pass
        if not title:
            return response_fail("Title is required")
        if request.user.is_authenticated:
            owner = request.user
        else:
            owner = User.objects.first()
            if not owner:
                return response_fail("No user found. Please create a user first.")
        due_date_ts = int(due_date.timestamp())
        current_time_ts = get_current_time_ts()
        task = Task.objects.create(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            project_id=project_id,
            executor_id=executor_id,
            owner=owner,
            end_time_ts=due_date_ts,
            start_time_ts=current_time_ts,
        )
        
        return response_success({"id": task.id, "title": task.title, "msg": "Created successfully"})
    
    except json.JSONDecodeError as e:
        return response_fail(e)
    except Exception as e:
        return response_fail(str(e))
  


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def task_detail(request, task_id):
    """
    GET    -> retrieve
    PUT    -> update
    DELETE -> delete
    """

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist as e:
        return response_fail(e)

    # GET
    if request.method == "GET":
        return response_success({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "owner": task.owner.username,
            "project_id": task.project_id,
            "executor_id": task.executor_id,
        })

    # PUT
    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            task.title = body.get("title", task.title)
            task.description = body.get("description", task.description)
            task.status = body.get("status", task.status)
            task.priority = body.get("priority", task.priority)
            if "project_id" in body:
                task.project_id = body.get("project_id")
            if "executor_id" in body:
                task.executor_id = body.get("executor_id")
            if "due_date" in body:
                try:
                    task.due_date = datetime.datetime.fromisoformat(body.get("due_date").replace("Z", "+00:00"))
                except:
                    pass
            
            task.save()
            return response_success({
                "id": task.id, 
                "title": task.title, 
                "msg": "Updated Successfully"
            })

        except json.JSONDecodeError as e:
            return response_fail(e.msg)
        except Exception as e:
            return response_fail(str(e))

    # DELETE
    if request.method == "DELETE":
        task.delete()
        return response_success({"deleted": True})
    


