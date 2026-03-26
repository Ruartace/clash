from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import TransactionSerializer
from . import services
from utils.response import success, error


class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filters = {
            'transaction_type': request.query_params.get('type'),
            'category': request.query_params.get('category'),
            'start_date': request.query_params.get('start_date'),
            'end_date': request.query_params.get('end_date'),
        }
        transactions = services.get_user_transactions(request.user, filters)
        serializer = TransactionSerializer(transactions, many=True)
        return success(data=serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        tx = services.create_transaction(request.user, serializer.validated_data)
        return success(data=TransactionSerializer(tx).data, message='创建成功', status=201)


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_tx(self, user, pk):
        return services.get_user_transactions(user).filter(pk=pk).first()

    def get(self, request, pk):
        tx = self._get_tx(request.user, pk)
        if not tx:
            return error(message='记录不存在', code=404, status=404)
        return success(data=TransactionSerializer(tx).data)

    def delete(self, request, pk):
        tx = self._get_tx(request.user, pk)
        if not tx:
            return error(message='记录不存在', code=404, status=404)
        services.delete_transaction(tx)
        return success(message='删除成功')
