from django.urls import path

from base.views import *

urlpatterns = [
    path('/product/<int:id>', TelephoneGetItemPatchDeleteAPIView.as_view(), name='telephone'),
    path('/product', TelephoneGetPostAPIView.as_view(), name='telephones'),
    path('/filters', FiltersForTelephoneGetAPIView.as_view(), name='filters'),

    path('/product_by_ids', TelephoneGetListAPIView.as_view(), name='list_telephones'),

    path('/brand', BrandGetPostAPIView.as_view(), name='brands'),
    path('/brand/<int:id>', BrandGetItemPatchDeleteAPIView.as_view(), name='brand'),

    path('/city', CityAPIView.as_view(), name='cities'),

    path('/user/self', UsersAuthenticatedGetPatchAPIView.as_view(), name='self-user'),
    path('/order/self', OrderGetSelfAPIView.as_view(), name='self-order'),

    path('/user', UsersAdminGetAPIView.as_view(), name='users_for_admin'),
    path('/user/<int:id>', UsersAdminGetItemPatchDeleteAPIView.as_view(), name='user_for_admin'),

    path('/order', OrderPostAPIView.as_view(), name='order'),
    path('/admin/order', OrderGetAPIView.as_view(), name='orders'),
    path('/order/<int:id>', OrderGetItemPatchAPIView.as_view(), name='order'),

    path('/vendor', VendorGetPostAPIView.as_view(), name='vendors'),
    path('/vendor/<int:id>', VendorGetPatchDeleteItemAPIView.as_view(), name='vendor'),

    path('/delivery', DeliveryGetPostAPIView.as_view(), name='deliveries'),
    path('/delivery/<int:id>', DeliveryGetPatchDeleteItemAPIView.as_view(), name='delivery'),
    path('/delivery_details/<int:id>', DeliveryDetailsPatch.as_view(), name='delivery_details'),

    path('/comment', CommentGetPostAPIView.as_view(), name='comment'),
    path('/comment/<int:id>', CommentPatchAPIView.as_view(), name='comment'),

    path('/wish_list', WishListAPIView.as_view(), name='wish_list'),
    path('/wish_list/<int:id>', WishListAPIView.as_view(), name='wish_list'),

    path('/analytic/views', ViewsGetFullDataAPIView.as_view(), name='analytic_views'),
    path('/analytic/avg_order_cost', OrderGetStatAVGCostAPIView.as_view(), name='analytic_avg_order_cost'),
    path('/analytic/order_amount_product', OrderGetStatAmountProductAPIView.as_view(), name='analytic_order_amount_product'),
    path('/analytic/order_amount', OrderGetStatAmountOrderAPIView.as_view(), name='analytic_order_amount'),
    path('/analytic/order_total_sum', OrderGetTotalSumAPIView.as_view(), name='analytic_order_total_sum'),
    path('/analytic/product_percent_sells', ProductGetPercentSellsAPIView.as_view(), name='analytic_order_total_sum'),

    path('/analytic/best_selling_telephone', BestSellingTelephoneAPIView.as_view(), name='analytic_best_selling_telephone'),
    path('/analytic/more_than_in_wish_list', MoreThanWishListAPIView.as_view(), name='analytic_more_than_in_wish_list'),
    path('/analytic/vendors_by_telephones_brand', VendorsByTelephonesBrandAPIView.as_view(), name='analytic_vendors_by_telephones_brand'),
    path('/analytic/users_by_quantity_and_total_cost_order', UsersByQuantityAndTotalCostOrderAPIView.as_view(), name='analytic_users_by_quantity_and_total_cost_order'),
    path('/analytic/users_placed_order_on_date', UsersPlacedOrderOnDateAPIView.as_view(), name='analytic_users_placed_order_on_date'),
]

