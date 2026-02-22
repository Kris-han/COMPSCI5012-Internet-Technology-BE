# tasks/api_utils.py
from __future__ import annotations

from typing import Any, Optional
from utils.code import ResponseCode
from django.http import JsonResponse



def response_success(data: Any = None, *, message: str = "OK", status: int = ResponseCode.SUCCESS) -> JsonResponse:
    """
    Unified success response envelope.

    Example:
    {
      "success": true,
      "data": {...},
      "error": null,
      "message": "OK"
      "status": 200
    }
    """
    return JsonResponse(
        {"success": True, "data": data, "error": None, "message": message, "status": status},
        status=status,
        json_dumps_params={"ensure_ascii": False},
    )


def response_fail(
    code: str,
    message: str,
    *,
    status: int = ResponseCode.BAD_REQUEST,
    details: Optional[Any] = None,
) -> JsonResponse:
    """
    Unified error response envelope.

    Example:
    {
      "success": false,
      "data": null,
      "error": {"code": "VALIDATION_ERROR", "message": "...", "details": {...}},
      "message": "..."
      "status": 400
    }
    """
    return JsonResponse(
        {
            "success": False,
            "data": None,
            "error": {"code": code, "message": message, "details": details},
            "message": message,
            "status": status,
        },
        status=status,
        json_dumps_params={"ensure_ascii": False},
    )