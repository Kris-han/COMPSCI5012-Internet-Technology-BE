from django.urls import path
from .views import hello, add_task, task_detail, task_list, search_task

urlpatterns = [
    path('hello/', hello),
    path('add_task', add_task),
    path('task_detail/<int:task_id>', task_detail),
    path('task_list', task_list),
    path('search_task', search_task),
]