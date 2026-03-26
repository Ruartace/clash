from .models import Asset


def get_user_assets(user):
    """获取用户所有资产（未删除）"""
    return Asset.objects.filter(user=user, is_deleted=False)


def create_asset(user, validated_data: dict) -> Asset:
    """创建资产"""
    return Asset.objects.create(user=user, **validated_data)


def update_asset(asset: Asset, validated_data: dict) -> Asset:
    """更新资产"""
    for key, value in validated_data.items():
        setattr(asset, key, value)
    asset.save()
    return asset


def delete_asset(asset: Asset) -> None:
    """软删除资产"""
    asset.is_deleted = True
    asset.save(update_fields=['is_deleted', 'updated_at'])
