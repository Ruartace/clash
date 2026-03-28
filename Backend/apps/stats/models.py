from django.conf import settings
from django.db import models


class FlowRecord(models.Model):
    """资金流向记录（用于资金流向图与资产网络补充关系）"""

    NODE_TYPE_CHOICES = [
        ('income', '收入'),
        ('account', '账户'),
        ('expense', '支出'),
        ('asset', '资产'),
        ('liability', '负债'),
        ('goal', '目标'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='flow_records',
    )
    source_name = models.CharField(max_length=100, verbose_name='来源名称')
    source_type = models.CharField(max_length=20, choices=NODE_TYPE_CHOICES, verbose_name='来源类型')
    target_name = models.CharField(max_length=100, verbose_name='去向名称')
    target_type = models.CharField(max_length=20, choices=NODE_TYPE_CHOICES, verbose_name='去向类型')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='金额')
    flow_date = models.DateField(verbose_name='流向日期')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stats_flow_records'
        verbose_name = '资金流向记录'
        verbose_name_plural = '资金流向记录'
        ordering = ['-flow_date', '-created_at']

    def __str__(self):
        return f'{self.user_id}: {self.source_name} -> {self.target_name} ({self.amount})'
