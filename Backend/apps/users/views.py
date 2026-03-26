from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer, UserSerializer
from . import services
from utils.response import success, error


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='注册信息有误', data=serializer.errors, code=400)
        data = services.register_user(serializer.validated_data)
        return success(data=data, message='注册成功', code=201, status=201)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success(data=serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        serializer.save()
        return success(data=serializer.data, message='更新成功')
