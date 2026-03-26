from .models import Goal


def get_user_goals(user):
    """获取用户所有目标（未删除）"""
    return Goal.objects.filter(user=user, is_deleted=False)


def create_goal(user, validated_data: dict) -> Goal:
    """创建财务目标"""
    return Goal.objects.create(user=user, **validated_data)


def update_goal(goal: Goal, validated_data: dict) -> Goal:
    """更新目标进度或信息"""
    for key, value in validated_data.items():
        setattr(goal, key, value)
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'
    goal.save()
    return goal


def delete_goal(goal: Goal) -> None:
    """软删除目标"""
    goal.is_deleted = True
    goal.save(update_fields=['is_deleted', 'updated_at'])
