from django.urls import path

from base.views import TelephoneAPIView, BrandAPIView, AuthenticatedUsersAPIView, AdminUsersAPIView

urlpatterns = [
    path('shop/<int:telephone_id>/', TelephoneAPIView.as_view()),
    path('shop/', TelephoneAPIView.as_view()),

    path('brand/<int:brand_id>/', BrandAPIView.as_view()),
    path('brand/', BrandAPIView.as_view()),

    path('user/', AuthenticatedUsersAPIView.as_view()),

    path('admin/user/', AdminUsersAPIView.as_view()),
    path('admin/user/<int:user_id>/', AdminUsersAPIView.as_view()),
]
