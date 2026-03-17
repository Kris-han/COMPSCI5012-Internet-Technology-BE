import json
import re
from utils.response import response_fail, response_success
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password, check_password

from .models import User, UserToken

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


@csrf_exempt
@require_http_methods(["POST"])
def register(request):

    try:
        body = json.loads(request.body or "{}")
    except Exception:
        return response_fail("Invalid JSON body")

    username = str(body.get("username", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", "")).strip()

    if not username:
        return response_fail("Username is required")

    if len(username) < 2 or len(username) > 50:
        return response_fail("Username length must be 2-50 characters")

    if not email:
        return response_fail("Email is required")

    if not is_valid_email(email):
        return response_fail("Invalid email format")

    if not password:
        return response_fail("Password is required")

    if len(password) < 6:
        return response_fail("Password must be at least 6 characters")

    if User.objects.filter(username=username).exists():
        return response_fail("Username already exists")

    if User.objects.filter(email=email).exists():
        return response_fail("Email already exists")

    user = User.objects.create(
        username=username,
        email=email,
        password_hash=make_password(password),
        avatar="",
        is_active=True,
    )

    token = UserToken.generate_token()
    UserToken.objects.create(
        user=user,
        token=token
    )

    return response_success({
        "token": token,
        "user_info": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar or "",
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        body = json.loads(request.body or "{}")
    except Exception:
        return response_fail("Invalid JSON body")

    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", "")).strip()

    if not email:
        return response_fail("Email is required")

    if not password:
        return response_fail("Password is required")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return response_fail("Email or password is incorrect", 401)

    if not user.is_active:
        return response_fail("User is disabled", 403)

    if not check_password(password, user.password_hash):
        return response_fail("Email or password is incorrect", 401)

    token = UserToken.generate_token()
    UserToken.objects.create(
        user=user,
        token=token
    )

    return response_success({
        "token": token,
        "user_info": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar or "",
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        return response_fail("Token is required", 401)

    UserToken.objects.filter(token=token).delete()
    return response_success()



@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return response_fail("Invalid JSON body")

    email = str(body.get("email", "")).strip().lower()
    new_password = str(body.get("new_password", "")).strip()
    confirm_password = str(body.get("confirm_password", "")).strip()

    if not email:
        return response_fail("Email is required")

    if not new_password:
        return response_fail("New password is required")

    if len(new_password) < 6:
        return response_fail("Password must be at least 6 characters")

    if new_password != confirm_password:
        return response_fail("The two passwords do not match")

    try:
        user = User.objects.get(email=email)
        if not user:
            return response_fail("User does not exist.", 401)
    except User.DoesNotExist:
        return response_fail("User does not exist", code=404)

    user.password_hash = make_password(new_password)
    user.save(update_fields=["password_hash"])

    return response_success()

