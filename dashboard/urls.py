from django.urls import path
from .views import dashboard_list, due_list, task_list

urlpatterns = [
    path('dashboard_list/', dashboard_list),
    path('due_list/', due_list),
    path('task_list/', task_list),

]