from .models import Account


def get_user_accounts(user):
    """获取用户所有账户（未删除）"""
    return Account.objects.filter(user=user, is_deleted=False)


def create_account(user, validated_data: dict) -> Account:
    """创建账户"""
    return Account.objects.create(user=user, **validated_data)


def update_account(account: Account, validated_data: dict) -> Account:
    """更新账户"""
    for key, value in validated_data.items():
        setattr(account, key, value)
    account.save()
    return account


def delete_account(account: Account) -> None:
    """软删除账户"""
    account.is_deleted = True
    account.save(update_fields=['is_deleted', 'updated_at'])
