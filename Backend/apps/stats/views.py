from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from . import services
from utils.response import success, error


class NetWorthView(APIView):
    """净资产统计"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = services.get_net_worth(request.user)
        return success(data=data)


class MonthlySummaryView(APIView):
    """月度收支汇总"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        if not year or not month:
            return error(message='请提供 year 和 month 参数')
        data = services.get_monthly_summary(request.user, int(year), int(month))
        return success(data=data)


class ExpenseByCategoryView(APIView):
    """分类支出统计"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        if not year or not month:
            return error(message='请提供 year 和 month 参数')
        data = services.get_expense_by_category(request.user, int(year), int(month))
        return success(data=data)
