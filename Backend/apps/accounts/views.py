from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import AccountSerializer
from . import services
from utils.response import success, error


class AccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = services.get_user_accounts(request.user)
        serializer = AccountSerializer(accounts, many=True)
        return success(data=serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        account = services.create_account(request.user, serializer.validated_data)
        return success(data=AccountSerializer(account).data, message='创建成功', status=201)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_account(self, user, pk):
        accounts = services.get_user_accounts(user)
        return accounts.filter(pk=pk).first()

    def get(self, request, pk):
        account = self._get_account(request.user, pk)
        if not account:
            return error(message='账户不存在', code=404, status=404)
        return success(data=AccountSerializer(account).data)

    def patch(self, request, pk):
        account = self._get_account(request.user, pk)
        if not account:
            return error(message='账户不存在', code=404, status=404)
        serializer = AccountSerializer(account, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        account = services.update_account(account, serializer.validated_data)
        return success(data=AccountSerializer(account).data, message='更新成功')

    def delete(self, request, pk):
        account = self._get_account(request.user, pk)
        if not account:
            return error(message='账户不存在', code=404, status=404)
        services.delete_account(account)
        return success(message='删除成功')
