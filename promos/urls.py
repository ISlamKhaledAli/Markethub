from django.urls import path

from promos.views import (
    AdminPromoDetailView,
    AdminPromoListCreateView,
    PromoApplyView,
    PromoValidateView,
)

urlpatterns = [
    path('validate/', PromoValidateView.as_view(), name='promo-validate'),
    path('apply/', PromoApplyView.as_view(), name='promo-apply'),
    path('<int:pk>/', AdminPromoDetailView.as_view(), name='promo-detail'),
    path('', AdminPromoListCreateView.as_view(), name='promo-list-create'),
]
