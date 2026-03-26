from django.db import models
from django.conf import settings


class Budget(models.Model):
    """月度预算"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='budgets'
    )
    category = models.CharField(max_length=50, verbose_name='分类')
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='预算金额'
    )
    year = models.IntegerField(verbose_name='年份')
    month = models.IntegerField(verbose_name='月份')
    note = models.TextField(blank=True, default='', verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'
        verbose_name = '预算'
        verbose_name_plural = '预算'
        unique_together = ('user', 'category', 'year', 'month')
        ordering = ['-year', '-month']

    def __str__(self):
        return f'{self.user.email} - {self.category} - {self.year}/{self.month}'
