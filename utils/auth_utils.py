from users.models import UserToken


def get_request_token(request):
    auth_header = request.headers.get("Authorization", "").strip()

    if not auth_header:
        return ""

    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "", 1).strip()

    return auth_header


def get_request_user(request):
    token = get_request_token(request)
    if not token:
        return None

    token_obj = UserToken.objects.select_related("user").filter(token=token).first()
    if not token_obj:
        return None

    if not token_obj.user.is_active:
        return None

    return token_obj.user