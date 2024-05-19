from django.urls import path

from base.views import AuthenticatedUsersAPIView, \
    AdminUsersPatchDeleteAPIView, AdminUsersGetAPIView, TelephonePatchPostDeleteAPIView, TelephoneGetAPIView, \
    BrandGetAPIView, BrandPostPatchDeleteAPIView

urlpatterns = [
    path('product/<int:telephone_id>/', TelephoneGetAPIView.as_view(), name='telephones'),
    path('product/<int:telephone_id>/', TelephonePatchPostDeleteAPIView.as_view(), name='telephones'),
    path('product/', TelephoneGetAPIView.as_view(), name='telephones'),

    path('brand/<int:brand_id>/', BrandGetAPIView.as_view(), name='brands'),
    path('brand/<int:brand_id>/', BrandPostPatchDeleteAPIView.as_view(), name='brands'),
    path('brand/', BrandGetAPIView.as_view(), name='brands'),

    path('user/', AuthenticatedUsersAPIView.as_view(), name='user'),

    path('admin/user/', AdminUsersGetAPIView.as_view(), name='user_for_admin'),
    path('admin/user/<int:user_id>/', AdminUsersGetAPIView.as_view(), name='user_for_admin'),
    path('admin/user/<int:user_id>/', AdminUsersPatchDeleteAPIView.as_view(), name='user_for_admin'),
]
