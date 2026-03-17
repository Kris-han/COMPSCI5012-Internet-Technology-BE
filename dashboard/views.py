import json
import math
import time
import calendar
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from utils.time import get_current_time_ts,get_month_ts
from utils.response import response_success, response_fail
from django.views.decorators.http import require_http_methods

from tasks.models import Task



@csrf_exempt
@require_http_methods(["GET"])
def dashboard_list(request):
    try:
        uid = request.GET.get("uid", "")
        if not uid:
            return response_fail("parameter is wrong!")

        uid = int(uid)

        now_ts = int(time.time())
        end_24h_ts = now_ts + 24 * 60 * 60
        end_7d_ts = now_ts + 7 * 24 * 60 * 60
        end_14d_ts = now_ts + 14 * 24 * 60 * 60
        month_start_ts, month_end_ts = get_month_ts()

        tasks = Task.objects.filter(uid=uid,is_deleted=0)
        total_tasks = tasks.count()
        completed_count = tasks.filter(status=Task.Status.COMPLETED).count()
        in_progress_count = tasks.filter(status=Task.Status.IN_PROGRESS).count()
        todo_count = tasks.filter(status=Task.Status.TODO).count()
        postponed_count = tasks.filter(status=Task.Status.POSTPONED).count()

        due_tasks = tasks.filter(end_time_ts__gte=now_ts)

        within_24_hours = due_tasks.filter(end_time_ts__lte=end_24h_ts).count()
        within_7_days = due_tasks.filter(end_time_ts__lte=end_7d_ts).count()
        within_14_days = due_tasks.filter(end_time_ts__lte=end_14d_ts).count()
        within_month = due_tasks.filter(end_time_ts__lte=month_end_ts).count()

        completed_last_24_hours = tasks.filter(
            completed_at_ts__isnull=False,
            completed_at_ts__gte=now_ts - 24 * 60 * 60
        ).count()

        postponed_this_week = tasks.filter(
            status=Task.Status.POSTPONED,
            end_time_ts__gte=now_ts,
            end_time_ts__lte=end_7d_ts
        ).count()

        result_data = {
            "summary": {
                "total_tasks": total_tasks,
                "completed": completed_count,
                "in_progress": in_progress_count,
                "postponed": postponed_count
            },
            "due_stats": {
                "within_24_hours": within_24_hours,
                "within_7_days": within_7_days,
                "within_14_days": within_14_days,
                "within_month": within_month
            },
            "status_stats": {
                "completed": completed_count,
                "in_progress": in_progress_count,
                "todo": todo_count,
                "postponed": postponed_count
            },
            "recent_summary": {
                "completed_last_24_hours": completed_last_24_hours,
                "in_progress_now": in_progress_count,
                "postponed_this_week": postponed_this_week
            }
        }

        return response_success(result_data)

    except Exception as e:
        return response_fail(str(e))


@csrf_exempt
@require_http_methods(["POST"])
def task_list(request):
    try:
        para = json.loads(request.body or "{}")
        data = para.get("params", {})
        uid = data.get("uid", "")
        if not uid:
            return response_fail("parameter is wrong!")

        page_size = int(data.get("page_size", 12))
        page = int(data.get("page", 1))
        keyword = str(data.get("keyword", "")).strip()
        status = data.get("status", "")
        project_id = data.get("project_id", "")

        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 12

        current_time_ts = get_current_time_ts()
        offset = (page - 1) * page_size

        queryset = Task.objects.filter(
            uid=uid,
            is_deleted=0,
            end_time_ts__gt=current_time_ts
        )

        if keyword:
            queryset = queryset.filter(title__icontains=keyword)

        if status not in ["", None]:
            queryset = queryset.filter(status=int(status))

        if project_id not in ["", None]:
            queryset = queryset.filter(project_id=int(project_id))

        queryset = queryset.order_by("end_time_ts", "-id")

        total = queryset.count()
        page_queryset = queryset[offset: offset + page_size]

        result_data = []
        for task in page_queryset:
            result_data.append({
                "id": task.id,
                "uid": task.uid,
                "title": task.title,
                "description": task.description,
                "project_id": task.project_id,
                "project_name": f"Project {task.project_id}" if task.project_id else "project",
                "status": task.status,
                "status_text": get_status_text(task.status),
                "priority": task.priority,
                "priority_text": get_priority_text(task.priority),
                "start_time_ts": task.start_time_ts,
                "end_time_ts": task.end_time_ts,
                "start_time_text": format_ts(task.start_time_ts),
                "end_time_text": format_ts(task.end_time_ts),
                "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else "",
                "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M:%S") if task.updated_at else "",
            })

        return response_success({
            "list": result_data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": offset + page_size < total,
            "total_pages": math.ceil(total / page_size) if page_size else 0
        })

    except Exception as e:
        return response_fail(str(e))


def format_ts(ts):
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime("%d-%m-%Y")


def get_status_text(status):
    status_map = {
        Task.Status.TODO: "To Do",
        Task.Status.IN_PROGRESS: "In Progress",
        Task.Status.COMPLETED: "Completed",
        Task.Status.POSTPONED: "Postponed",
    }
    return status_map.get(status, "")


def get_priority_text(priority):
    priority_map = {
        Task.Priority.LOW: "Low",
        Task.Priority.MEDIUM: "Medium",
        Task.Priority.HIGH: "High",
    }
    return priority_map.get(priority, "")

