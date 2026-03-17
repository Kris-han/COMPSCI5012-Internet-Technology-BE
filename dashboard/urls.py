from django.urls import path
from .views import dashboard_list, task_list,finished_list, finished_reopen, finished_delete

urlpatterns = [
    path('dashboard_list', dashboard_list),
    path('task_list', task_list),
    path('finished_list', finished_list),
    path('finished_reopen', finished_reopen),
    path('finished_delete', finished_delete),

]