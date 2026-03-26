from django.db.models import Sum
from .models import Budget
from apps.transactions.models import Transaction


def get_user_budgets(user, year: int = None, month: int = None):
    """获取用户预算，可按年月过滤"""
    qs = Budget.objects.filter(user=user)
    if year:
        qs = qs.filter(year=year)
    if month:
        qs = qs.filter(month=month)
    return qs


def create_budget(user, validated_data: dict) -> Budget:
    """创建预算"""
    return Budget.objects.create(user=user, **validated_data)


def get_budget_usage(user, year: int, month: int) -> list:
    """计算各分类预算使用情况"""
    budgets = Budget.objects.filter(user=user, year=year, month=month)
    result = []
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=user,
            category=budget.category,
            transaction_type='expense',
            transaction_date__year=year,
            transaction_date__month=month,
            is_deleted=False,
        ).aggregate(total=Sum('amount'))['total'] or 0
        result.append({
            'category': budget.category,
            'budget': str(budget.amount),
            'spent': str(spent),
            'remaining': str(budget.amount - spent),
        })
    return result
