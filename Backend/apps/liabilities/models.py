from django.db import models
from django.conf import settings


class Liability(models.Model):
    """负债记录"""

    LIABILITY_TYPE_CHOICES = [
        ('mortgage', '房贷'),
        ('car_loan', '车贷'),
        ('credit_card', '信用卡欠款'),
        ('personal_loan', '个人借款'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='liabilities'
    )
    name = models.CharField(max_length=100, verbose_name='负债名称')
    liability_type = models.CharField(max_length=20, choices=LIABILITY_TYPE_CHOICES)
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='总金额'
    )
    remaining_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='剩余金额'
    )
    interest_rate = models.DecimalField(
        max_digits=6, decimal_places=4, default=0, verbose_name='年利率'
    )
    due_date = models.DateField(null=True, blank=True, verbose_name='到期日')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'liabilities'
        verbose_name = '负债'
        verbose_name_plural = '负债'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.name}'
