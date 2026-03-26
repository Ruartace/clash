from .models import Liability


def get_user_liabilities(user):
    """获取用户所有负债（未删除）"""
    return Liability.objects.filter(user=user, is_deleted=False)


def create_liability(user, validated_data: dict) -> Liability:
    """创建负债"""
    return Liability.objects.create(user=user, **validated_data)


def update_liability(liability: Liability, validated_data: dict) -> Liability:
    """更新负债"""
    for key, value in validated_data.items():
        setattr(liability, key, value)
    liability.save()
    return liability


def delete_liability(liability: Liability) -> None:
    """软删除负债"""
    liability.is_deleted = True
    liability.save(update_fields=['is_deleted', 'updated_at'])
