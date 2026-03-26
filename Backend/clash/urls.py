"""
URL configuration for clash project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/transactions/', include('apps.transactions.urls')),
    path('api/assets/', include('apps.assets.urls')),
    path('api/liabilities/', include('apps.liabilities.urls')),
    path('api/budgets/', include('apps.budgets.urls')),
    path('api/goals/', include('apps.goals.urls')),
    path('api/statistics/', include('apps.stats.urls')),
]
