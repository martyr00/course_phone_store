from django.urls import path

from base.views import UsersAuthenticatedGetPatchAPIView, UsersAdminGetAPIView, TelephoneGetPostAPIView, \
    BrandGetPostAPIView, TelephoneGetItemPatchDeleteAPIView, BrandGetItemPatchDeleteAPIView, \
    UsersAdminGetItemPatchDeleteAPIView, TelephoneGetListAPIView, CityAPIView, OrderGetListByUserAPIView, \
    OrderGetPostAPIView, OrderGetItemPatchAPIView, OrderGetSelfAPIView

urlpatterns = [
    path('/product/<int:id>', TelephoneGetItemPatchDeleteAPIView.as_view(), name='telephone'),
    path('/product', TelephoneGetPostAPIView.as_view(), name='telephones'),

    path('/product_by_ids', TelephoneGetListAPIView.as_view(), name='list_telephones'),

    path('/brand/<int:id>', BrandGetItemPatchDeleteAPIView.as_view(), name='brand'),
    path('/brand', BrandGetPostAPIView.as_view(), name='brands'),

    path('/city', CityAPIView.as_view(), name='cities'),

    path('/user/self', UsersAuthenticatedGetPatchAPIView.as_view(), name='self-user'),
    path('/order/self', OrderGetSelfAPIView.as_view(), name='self-order'),

    path('/user', UsersAdminGetAPIView.as_view(), name='users_for_admin'),
    path('/user/<int:id>', UsersAdminGetItemPatchDeleteAPIView.as_view(), name='user_for_admin'),

    path('/order', OrderGetPostAPIView.as_view(), name='orders'),
    path('/order/<int:id>', OrderGetItemPatchAPIView.as_view(), name='order'),
    path('/order_by_user_id', OrderGetListByUserAPIView.as_view(), name='order_by_user_id'),
]