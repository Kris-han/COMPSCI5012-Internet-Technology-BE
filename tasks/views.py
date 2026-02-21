from utils.response import response
from utils.code import ResponseCode

def hello(request):
    data = {
        "user": "chris",
        "project": "COMPSCI5012",
        "status": "Backend ready"
    }
    return response(
        code = ResponseCode.SUCCESS,
        message = "Hello, Django backend is working!",
        data=data
    )

