from django.db.models import Sum, Q
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.assets.models import Asset
from apps.liabilities.models import Liability
from apps.accounts.models import Account


def get_net_worth(user) -> dict:
    """计算净资产 = 总资产 - 总负债"""
    total_assets = Asset.objects.filter(
        user=user, is_deleted=False
    ).aggregate(total=Sum('current_value'))['total'] or 0

    total_liabilities = Liability.objects.filter(
        user=user, is_deleted=False
    ).aggregate(total=Sum('remaining_amount'))['total'] or 0

    account_balance = Account.objects.filter(
        user=user, is_deleted=False
    ).aggregate(total=Sum('balance'))['total'] or 0

    return {
        'total_assets': str(total_assets + account_balance),
        'total_liabilities': str(total_liabilities),
        'net_worth': str(total_assets + account_balance - total_liabilities),
    }


def get_monthly_summary(user, year: int, month: int) -> dict:
    """获取指定月份收支汇总"""
    base_qs = Transaction.objects.filter(
        user=user,
        transaction_date__year=year,
        transaction_date__month=month,
        is_deleted=False,
    )
    income = base_qs.filter(transaction_type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0
    expense = base_qs.filter(transaction_type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0
    return {
        'year': year,
        'month': month,
        'income': str(income),
        'expense': str(expense),
        'balance': str(income - expense),
    }


def get_yearly_summary(user, year: int) -> list:
    """获取指定年份全年各月收支汇总"""
    result = []
    for month in range(1, 13):
        data = get_monthly_summary(user, year, month)
        result.append(data)
    return result


def get_expense_by_category(user, year: int, month: int) -> list:
    """获取指定月份各分类支出占比"""
    qs = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        transaction_date__year=year,
        transaction_date__month=month,
        is_deleted=False,
    ).values('category').annotate(total=Sum('amount')).order_by('-total')
    return [{'category': item['category'], 'amount': str(item['total'])} for item in qs]
