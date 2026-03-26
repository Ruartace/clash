from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from . import services
from utils.response import success, error


class NetWorthView(APIView):
    """净资产统计"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = services.get_net_worth(request.user)
        return success(data=data)


class MonthlySummaryView(APIView):
    """月度收支汇总 - 传 year+month 返回单月，只传 year 返回全年列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        if not year:
            year = timezone.now().year
        if month:
            data = services.get_monthly_summary(request.user, int(year), int(month))
        else:
            data = services.get_yearly_summary(request.user, int(year))
        return success(data=data)


class YearlySummaryView(APIView):
    """全年收支汇总列表"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year', timezone.now().year)
        data = services.get_yearly_summary(request.user, int(year))
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
