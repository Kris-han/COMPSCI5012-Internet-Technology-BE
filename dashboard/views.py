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
        data = json.loads(request.body)

        uid = data.get("uid", "")
        if not uid:
            return  response_fail("parameter is wrong!")

        start_time_ts, end_time_ts = get_month_ts()
        queryset = Task.objects.filter(
            uid=uid,
            start_time_ts__lt=end_time_ts,
            end_time_ts__gt=start_time_ts
        )
        find_data = Task.objects.filter(queryset)
        result_data =  {}
        for one_data in find_data:
            if one_data.status == Task.Status.TODO:
                result_data["todo_data"] = data.get("todo_data", 0) + 1
            if one_data.status == Task.Status.IN_PROGRESS:
                result_data["doing_data"] = data.get("doing_data", 0) + 1
            if one_data.status == Task.Status.COMPLETED:
                result_data["finish_data"] = data.get("finish_data", 0) + 1
            if one_data.status == Task.Status.POSTPONED:
                result_data["delay_data"] = data.get("delay_data", 0) + 1

        return response_success(result_data)
    except Exception as e:
        return response_fail(str(e))


@csrf_exempt
@require_http_methods(["GET"])
def due_list(request):
    try:
        data = json.loads(request.body)

        uid = data.get("uid", "")
        if not uid:
            return  response_fail("parameter is wrong!")

        current_time_ts = get_current_time_ts()
        queryset = Task.objects.filter(
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

        find_data = Task.objects.filter(queryset)
        for one_data in find_data:
            due_ts = one_data.end_time_ts
            if due_ts <= end_24h_ts:
                data["24 hours"] += 1
            if due_ts <= end_7d_ts:
                data["7 days"] += 1
            if due_ts <= end_14d_ts:
                data["14 days"] += 1
            if due_ts <= month_end_ts:
                data["month"] += 1

        return response_success(result_data)
    except Exception as e:
        return response_fail(str(e))




