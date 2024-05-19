from django.urls import path

from base.views import AuthenticatedUsersAPIView, \
    AdminUsersPatchDeleteAPIView, AdminUsersGetAPIView, \
    TelephoneGetPostAPIView, \
    BrandGetPostAPIView, TelephoneGetItemPatchDeleteAPIView, BrandGetItemPatchDeleteAPIView

urlpatterns = [
    path('product/<int:id>/', TelephoneGetItemPatchDeleteAPIView.as_view(), name='telephones'),
    path('product/', TelephoneGetPostAPIView.as_view(), name='telephones'),

    path('brand/<int:id>/', BrandGetItemPatchDeleteAPIView.as_view(), name='brands'),
    path('brand/', BrandGetPostAPIView.as_view(), name='brands'),

    path('user/', AuthenticatedUsersAPIView.as_view(), name='user'),

    path('admin/user/', AdminUsersGetAPIView.as_view(), name='user_for_admin'),
    path('admin/user/<int:id>/', AdminUsersGetAPIView.as_view(), name='user_for_admin'),
    path('admin/user/<int:id>/', AdminUsersPatchDeleteAPIView.as_view(), name='user_for_admin'),
]