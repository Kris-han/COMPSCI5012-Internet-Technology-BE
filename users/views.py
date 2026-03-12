from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from utils.response import response_success


@require_http_methods(["GET"])
def user_list(request):
    users = User.objects.values('id', 'username').order_by('id')
    return response_success(list(users))
