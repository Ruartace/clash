from django.db.models import Sum, Q
from .models import Transaction
from apps.accounts.models import Account


def get_user_transactions(user, filters: dict = None):
    """获取用户流水，支持按类型/分类/日期过滤"""
    qs = Transaction.objects.filter(user=user, is_deleted=False)
    if filters:
        if filters.get('transaction_type'):
            qs = qs.filter(transaction_type=filters['transaction_type'])
        if filters.get('category'):
            qs = qs.filter(category=filters['category'])
        if filters.get('start_date'):
            qs = qs.filter(transaction_date__gte=filters['start_date'])
        if filters.get('end_date'):
            qs = qs.filter(transaction_date__lte=filters['end_date'])
    return qs


def create_transaction(user, validated_data: dict) -> Transaction:
    """创建流水并同步账户余额"""
    account: Account = validated_data['account']
    amount = validated_data['amount']
    t_type = validated_data['transaction_type']

    transaction = Transaction.objects.create(user=user, **validated_data)

    # 同步账户余额
    if t_type == 'income':
        account.balance += amount
    elif t_type == 'expense':
        account.balance -= amount
    account.save(update_fields=['balance', 'updated_at'])

    return transaction


def delete_transaction(transaction: Transaction) -> None:
    """软删除流水"""
    transaction.is_deleted = True
    transaction.save(update_fields=['is_deleted', 'updated_at'])
