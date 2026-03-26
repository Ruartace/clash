from django.urls import path
from .views import BudgetListCreateView, BudgetUsageView

urlpatterns = [
    path('', BudgetListCreateView.as_view(), name='budget-list'),
    path('usage/', BudgetUsageView.as_view(), name='budget-usage'),
]
