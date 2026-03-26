"""
统一响应工具函数
所有接口响应统一使用此模块，格式：{ code, message, data }
"""

from rest_framework.response import Response


def success(data=None, message='success', code=200, status=200):
    """成功响应"""
    return Response(
        {
            'code': code,
            'message': message,
            'data': data,
        },
        status=status,
    )


def error(message='error', code=400, data=None, status=400):
    """错误响应"""
    return Response(
        {
            'code': code,
            'message': message,
            'data': data,
        },
        status=status,
    )
