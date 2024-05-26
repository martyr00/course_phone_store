from django.urls import path

from base.views import AuthenticatedUsersAPIView, AdminUsersGetAPIView, TelephoneGetPostAPIView, \
    BrandGetPostAPIView, TelephoneGetItemPatchDeleteAPIView, BrandGetItemPatchDeleteAPIView, \
    AdminUsersGetItemPatchDeleteAPIView, TelephoneGetListAPIView, CityAPIView, GetListByUserOrderAPIView, \
    GetPostOrderAPIView, GetItemPatchOrderAPIView, GetSelfOrderAPIView

urlpatterns = [
    path('/product/<int:id>', TelephoneGetItemPatchDeleteAPIView.as_view(), name='telephone'),
    path('/product', TelephoneGetPostAPIView.as_view(), name='telephones'),

    path('/product_by_ids', TelephoneGetListAPIView.as_view(), name='list_telephones'),

    path('/brand/<int:id>', BrandGetItemPatchDeleteAPIView.as_view(), name='brand'),
    path('/brand', BrandGetPostAPIView.as_view(), name='brands'),

    path('/city', CityAPIView.as_view(), name='cities'),

    path('/user/self', AuthenticatedUsersAPIView.as_view(), name='self-user'),
    path('/order/self', GetSelfOrderAPIView.as_view(), name='self-order'),

    path('/user', AdminUsersGetAPIView.as_view(), name='users_for_admin'),
    path('/user/<int:id>', AdminUsersGetItemPatchDeleteAPIView.as_view(), name='user_for_admin'),

    path('/order', GetPostOrderAPIView.as_view(), name='orders'),
    path('/order/<int:id>', GetItemPatchOrderAPIView.as_view(), name='order'),
    path('/order_by_user_id', GetListByUserOrderAPIView.as_view(), name='order_by_user_id'),
]