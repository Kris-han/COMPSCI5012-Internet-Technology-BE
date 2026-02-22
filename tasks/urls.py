from django.urls import path
from .views import hello, add_task, task_detail

urlpatterns = [
    path('hello/', hello),
    path("add_task", add_task),
    path("task_detail/<int:task_id>", task_detail),

]