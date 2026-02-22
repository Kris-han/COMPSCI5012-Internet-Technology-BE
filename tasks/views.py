import json
from tasks.models import Task
from utils.code import ResponseCode
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
    except json.JSONDecodeError as e:
        return response_fail(e)

    title = body.get("title", "").strip()
    task = Task.objects.create(title=title)
    return response_success({"id": task.id, "title": task.title})


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

    if request.method == "GET":
        return response_success({"id": task.id, "title": task.title})

    if request.method == "PUT":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError as e:
            return response_fail(e.msg)

        title = body.get("title", "").strip()
        task.title = title
        task.save()
        return response_success({"id": task.id, "title": task.title})

    # DELETE
    task.delete()
    return response_success({"deleted": True})