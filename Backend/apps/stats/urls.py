from django.urls import path
from .views import NetWorthView, MonthlySummaryView, ExpenseByCategoryView

urlpatterns = [
    path('net-worth/', NetWorthView.as_view(), name='stats-net-worth'),
    path('monthly/', MonthlySummaryView.as_view(), name='stats-monthly'),
    path('expense-by-category/', ExpenseByCategoryView.as_view(), name='stats-expense-category'),
]
