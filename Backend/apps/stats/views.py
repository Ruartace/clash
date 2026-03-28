from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import services
from .serializers import FlowRecordSerializer
from utils.response import error, success


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


class FlowRecordListCreateView(APIView):
    """资金流向记录列表/写入"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        qs = services.get_flow_records(
            request.user,
            year=int(year) if year else None,
            month=int(month) if month else None,
        )
        return success(data=FlowRecordSerializer(qs, many=True).data)

    def post(self, request):
        serializer = FlowRecordSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message='数据有误', data=serializer.errors)
        item = services.create_flow_record(request.user, serializer.validated_data)
        return success(data=FlowRecordSerializer(item).data, message='创建成功', status=201)


class FlowGraphView(APIView):
    """资金流向图数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        data = services.get_flow_graph(
            request.user,
            year=int(year) if year else None,
            month=int(month) if month else None,
        )
        return success(data=data)


class HeatmapView(APIView):
    """热力图数据（income/expense/net）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year', timezone.now().year)
        mode = request.query_params.get('mode', 'expense')
        if mode not in ['income', 'expense', 'net']:
            return error(message='mode 仅支持 income/expense/net')
        data = services.get_heatmap_data(request.user, int(year), mode)
        return success(data=data)


class AssetNetworkView(APIView):
    """资产网络图数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = services.get_asset_network(request.user)
        return success(data=data)
