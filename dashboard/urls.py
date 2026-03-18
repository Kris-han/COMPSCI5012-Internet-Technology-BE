from django.urls import path
from .views import dashboard_list, task_list, finished_list, finished_reopen, finished_delete, today_count, \
    get_random_quote, get_daily_quote

urlpatterns = [
    path('dashboard_list', dashboard_list),
    path('task_list', task_list),
    path('finished_list', finished_list),
    path('finished_reopen', finished_reopen),
    path('finished_delete', finished_delete),
    path('today_count', today_count),
    path('get_random_quote', get_random_quote),
    path('get_daily_quote', get_daily_quote),

]