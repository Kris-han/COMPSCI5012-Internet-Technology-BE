from .code import ResponseCode
from typing import Any, Optional
from django.http import JsonResponse



def response_success(data: Any = None,code: int = ResponseCode.SUCCESS,) -> JsonResponse:
    """
    Unified success response.

    Example:
    {
        "success": true,
        "code": 0,
        "data": {...},
    }
    """
    return JsonResponse(
        {
            "success": True,
            "code": code,
            "data": data,
        }
    )


def response_fail(message: str=None, code: int=ResponseCode.BAD_REQUEST) -> JsonResponse:
    """
    Unified error response.

    Example:
    {
        "success": false,
        "code": 1001,
        "message": "Validation error",
    }
    """
    return JsonResponse(
        {
            "success": False,
            "code": code,          # 业务错误码，例如 1001
            "message": message,
        }
    )