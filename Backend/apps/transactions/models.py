from django.db import models
from django.conf import settings


class Transaction(models.Model):
    """收支流水记录"""

    TYPE_CHOICES = [
        ('income', '收入'),
        ('expense', '支出'),
        ('transfer', '转账'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='transactions'
    )
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.PROTECT, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='金额')
    category = models.CharField(max_length=50, verbose_name='分类')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    transaction_date = models.DateField(verbose_name='交易日期')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = '流水'
        verbose_name_plural = '流水'
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.transaction_type} - {self.amount}'
