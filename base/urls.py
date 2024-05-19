from django.urls import path

from base.views import AuthenticatedUsersAPIView, \
    AdminUsersPatchDeleteAPIView, AdminUsersGetAPIView, TelephonePostAPIView, TelephoneGetAPIView, \
    TelephonePatchDeleteAPIView, BrandPostAPIView, BrandGetAPIView, BrandPatchDeleteAPIView

urlpatterns = [
    path('product/<int:id>/', TelephoneGetAPIView.as_view(), name='telephones'),
    path('product/<int:id>/', TelephonePatchDeleteAPIView.as_view(), name='telephones'),
    path('product/', TelephonePostAPIView.as_view(), name='telephones'),
    path('product/', TelephoneGetAPIView.as_view(), name='telephones'),

    path('brand/<int:id>/', BrandGetAPIView.as_view(), name='brands'),
    path('brand/<int:id>/', BrandPatchDeleteAPIView.as_view(), name='brands'),
    path('brand/', BrandGetAPIView.as_view(), name='brands'),
    path('brand/', BrandPostAPIView.as_view(), name='brands'),

    path('user/', AuthenticatedUsersAPIView.as_view(), name='user'),

    path('admin/user/', AdminUsersGetAPIView.as_view(), name='user_for_admin'),
    path('admin/user/<int:id>/', AdminUsersGetAPIView.as_view(), name='user_for_admin'),
    path('admin/user/<int:id>/', AdminUsersPatchDeleteAPIView.as_view(), name='user_for_admin'),
]
