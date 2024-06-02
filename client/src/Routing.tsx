import React from 'react';
import { Route, Routes } from 'react-router-dom';

import Catalog from './pages/Catalog';
import Product from './pages/Product';
import Compare from './pages/Compare';
import Favorite from './pages/Favorite';
import Checkout from './pages/Checkout';
import Registration from './pages/Registration';
import NotFound from './pages/NotFound';
import SignIn from './pages/SignIn';

import Admin from './pages/admin/Admin';
import AdminAnalytic from './pages/admin/Analytic';
import AdminUsers from './pages/admin/Users';
import AdminUsersEdit from './pages/admin/UsersEdit';
import AdminProducts from './pages/admin/Products';
import AdminProductsCreateEdit from './pages/admin/ProductsCreateEdit';
import AdminOrders from './pages/admin/Orders';
import AdminOrdersEdit from './pages/admin/OrdersEdit';
import AdminDelivery from './pages/admin/Delivery';
import AdminDeliveryCreateEdit from './pages/admin/DeliveryCreateEdit';
import AdminVendor from './pages/admin/Vendor';
import AdminVendorCreateEdit from './pages/admin/VendorCreateEdit';

const Routing = () => (
	<Routes>
		<Route path="/" element={<Catalog />} />
		<Route path="/product/:id" element={<Product />} />
		<Route path="/compare" element={<Compare />} />
		<Route path="/favorite" element={<Favorite />} />
		<Route path="/checkout" element={<Checkout />} />

		<Route path="/registration" element={<Registration />} />
		<Route path="/login" element={<SignIn />} />

		<Route path="/admin" element={<Admin />}>
			<Route path="analytic" element={<AdminAnalytic />} />

			<Route path="user" element={<AdminUsers />} />
			<Route path="user/:id" element={<AdminUsersEdit />} />

			<Route path="product" element={<AdminProducts />} />
			<Route path="product/new" element={<AdminProductsCreateEdit />} />
			<Route path="product/:id" element={<AdminProductsCreateEdit />} />

			<Route path="order" element={<AdminOrders />} />
			<Route path="order/:id" element={<AdminOrdersEdit />} />

			<Route path="delivery" element={<AdminDelivery />} />
			<Route path="delivery/new" element={<AdminDeliveryCreateEdit />} />
			<Route path="delivery/:id" element={<AdminDeliveryCreateEdit />} />

			<Route path="vendor" element={<AdminVendor />} />
			<Route path="vendor/new" element={<AdminVendorCreateEdit />} />
			<Route path="vendor/:id" element={<AdminVendorCreateEdit />} />
		</Route>

		<Route path="*" element={<NotFound />} />
	</Routes>
);

export default Routing;