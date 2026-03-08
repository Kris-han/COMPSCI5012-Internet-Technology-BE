import json
import datetime
import calendar
from tasks.models import Task, Project
from utils.time import get_month_ts, get_current_time_ts
from django.views.decorators.csrf import csrf_exempt
from utils.response import response_success, response_fail
from django.views.decorators.http import require_http_methods



@csrf_exempt
@require_http_methods(["GET"])
def dashboard_list(request):
    try:
        uid = request.get.get("uid", "")
        if not uid:
            return  response_fail("parameter is wrong!")

        start_time_ts, end_time_ts = get_month_ts()
        find_data = Task.objects.filter(
            uid=uid,
            start_time_ts__lt=end_time_ts,
            end_time_ts__gt=start_time_ts
        )
        result_data =  {}
        for one_data in find_data:
            if one_data.status == Task.Status.TODO:
                result_data["todo_data"] = result_data.get("todo_data", 0) + 1
            if one_data.status == Task.Status.IN_PROGRESS:
                result_data["doing_data"] = result_data.get("doing_data", 0) + 1
            if one_data.status == Task.Status.COMPLETED:
                result_data["finish_data"] = result_data.get("finish_data", 0) + 1
            if one_data.status == Task.Status.POSTPONED:
                result_data["delay_data"] = result_data.get("delay_data", 0) + 1

        return response_success(result_data)
    except Exception as e:
        return response_fail(str(e))


@csrf_exempt
@require_http_methods(["GET"])
def due_list(request):
    try:
        uid = request.get.get("uid", "")
        if not uid:
            return  response_fail("parameter is wrong!")

        current_time_ts = get_current_time_ts()
        find_data = Task.objects.filter(
            uid=uid,
            end_time__gt=current_time_ts
        )
        end_24h_ts = current_time_ts + 24 * 60 * 60
        end_7d_ts = current_time_ts + 7 * 24 * 60 * 60
        end_14d_ts = current_time_ts + 14 * 24 * 60 * 60

        now_dt = datetime.datetime.now()
        last_day = calendar.monthrange(now_dt.year, now_dt.month)[1]

        month_end_dt = now_dt.replace(
            day=last_day,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999
        )
        month_end_ts = int(month_end_dt.timestamp())

        result_data = {
            "24_hours": 0,
            "7_days": 0,
            "14_days": 0,
            "month": 0,
        }
        for one_data in find_data:
            due_ts = one_data.end_time_ts
            if due_ts <= end_24h_ts:
                result_data["24 hours"] += 1
            if due_ts <= end_7d_ts:
                result_data["7 days"] += 1
            if due_ts <= end_14d_ts:
                result_data["14 days"] += 1
            if due_ts <= month_end_ts:
                result_data["month"] += 1

        return response_success(result_data)
    except Exception as e:
        return response_fail(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def task_list(request):
    try:
        data = json.loads(request.body)

        uid = data.get("uid", "")
        if not uid:
            return  response_fail("parameter is wrong!")
        page_size = int(data.get("page_size", 8))
        page_number = int(data.get("page_number", 1))

        current_time_ts = get_current_time_ts()
        offset = (page_number - 1) * page_size

        find_data = Task.objects.filter(
            uid=uid,
            end_time_ts__gt=current_time_ts
        ).order_by("end_time_ts")

        total = find_data.count()
        page_queryset = find_data[offset: offset + page_size]

        result_data = []
        for task in page_queryset:
            result_data.append({
                "id": task.id,
                "uid": task.uid,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "start_time_ts": task.start_time_ts,
                "end_time_ts": task.end_time_ts,
            })

        return response_success({
            "list": result_data,
            "total": total,
            "page_number": page_number,
            "page_size": page_size,
            "has_next": offset + page_size < total
        })

    except Exception as e:
        return response_fail(str(e))




