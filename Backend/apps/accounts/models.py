from django.db import models
from django.conf import settings


class Account(models.Model):
    """账户（储蓄卡、信用卡、支付宝等）"""

    ACCOUNT_TYPE_CHOICES = [
        ('cash', '现金'),
        ('debit_card', '储蓄卡'),
        ('credit_card', '信用卡'),
        ('alipay', '支付宝'),
        ('wechat', '微信钱包'),
        ('investment', '投资账户'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='accounts'
    )
    name = models.CharField(max_length=100, verbose_name='账户名称')
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='debit_card'
    )
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name='余额'
    )
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        verbose_name = '账户'
        verbose_name_plural = '账户'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.name}'
