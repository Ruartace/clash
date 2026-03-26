from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import BudgetSerializer
from . import services
from utils.response import success, error


class BudgetListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        # 支持 month=YYYY-MM 格式
        if month and '-' in month:
            parts = month.split('-')
            year = parts[0]
            month = parts[1]
        items = services.get_user_budgets(
            request.user,
            year=int(year) if year else None,
            month=int(month) if month else None,
        )
        return success(data=BudgetSerializer(items, many=True).data)

    def post(self, request):
        serializer = BudgetSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        item = services.create_budget(request.user, serializer.validated_data)
        return success(data=BudgetSerializer(item).data, message='创建成功', status=201)


class BudgetUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        if not year or not month:
            return error(message='请提供 year 和 month 参数')
        data = services.get_budget_usage(request.user, int(year), int(month))
        return success(data=data)
