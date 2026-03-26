from django.urls import path
from .views import NetWorthView, MonthlySummaryView, ExpenseByCategoryView, YearlySummaryView

urlpatterns = [
    path('net-worth/', NetWorthView.as_view(), name='stats-net-worth'),
    path('monthly/', MonthlySummaryView.as_view(), name='stats-monthly'),
    path('yearly/', YearlySummaryView.as_view(), name='stats-yearly'),
    path('expense-by-category/', ExpenseByCategoryView.as_view(), name='stats-expense-category'),
]
