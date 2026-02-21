from django.http import JsonResponse

def response(code=200, message="success", data=None):
    return JsonResponse({
            "code": code,
            "message": message,
            "data": data
        }, status=code
    )