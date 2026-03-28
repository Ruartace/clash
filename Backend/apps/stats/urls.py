from django.urls import path

from .views import (
    AssetNetworkView,
    ExpenseByCategoryView,
    FlowGraphView,
    FlowRecordListCreateView,
    HeatmapView,
    MonthlySummaryView,
    NetWorthView,
    YearlySummaryView,
)

urlpatterns = [
    path('net-worth/', NetWorthView.as_view(), name='stats-net-worth'),
    path('monthly/', MonthlySummaryView.as_view(), name='stats-monthly'),
    path('yearly/', YearlySummaryView.as_view(), name='stats-yearly'),
    path('expense-by-category/', ExpenseByCategoryView.as_view(), name='stats-expense-category'),
    path('flow-records/', FlowRecordListCreateView.as_view(), name='stats-flow-records'),
    path('flow-graph/', FlowGraphView.as_view(), name='stats-flow-graph'),
    path('heatmap/', HeatmapView.as_view(), name='stats-heatmap'),
    path('asset-network/', AssetNetworkView.as_view(), name='stats-asset-network'),
]
