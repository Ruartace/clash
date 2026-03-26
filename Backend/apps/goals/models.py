from django.db import models
from django.conf import settings


class Goal(models.Model):
    """财务目标"""

    STATUS_CHOICES = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('abandoned', '已放弃'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='goals'
    )
    name = models.CharField(max_length=100, verbose_name='目标名称')
    target_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='目标金额'
    )
    current_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name='当前金额'
    )
    deadline = models.DateField(null=True, blank=True, verbose_name='截止日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'goals'
        verbose_name = '财务目标'
        verbose_name_plural = '财务目标'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.name}'
