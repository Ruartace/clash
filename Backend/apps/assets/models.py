from django.db import models
from django.conf import settings


class Asset(models.Model):
    """资产记录（固定资产或金融资产）"""

    ASSET_TYPE_CHOICES = [
        ('real_estate', '房产'),
        ('vehicle', '车辆'),
        ('stock', '股票'),
        ('fund', '基金'),
        ('deposit', '存款'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='assets'
    )
    name = models.CharField(max_length=100, verbose_name='资产名称')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    current_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='当前价值'
    )
    purchase_value = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='购入价值'
    )
    purchase_date = models.DateField(verbose_name='购入日期')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assets'
        verbose_name = '资产'
        verbose_name_plural = '资产'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.name}'
