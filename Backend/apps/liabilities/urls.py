from django.urls import path
from .views import LiabilityListCreateView, LiabilityDetailView

urlpatterns = [
    path('', LiabilityListCreateView.as_view(), name='liability-list'),
    path('<int:pk>/', LiabilityDetailView.as_view(), name='liability-detail'),
]
