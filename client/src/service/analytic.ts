import api from '../utils/api';
import { IAnalyticItem } from '../utils/types';

export const getAnalyticView = async () => {
	const res = await api.get<IAnalyticItem[]>('/api/v1/analytic/views');

	return res.data;
};

export const getAnalyticAvgOrderCost = async () => {
	const res = await api.get<IAnalyticItem[]>('/api/v1/analytic/avg_order_cost');

	return res.data;
};

export const getAnalyticOrderAmount = async () => {
	const res = await api.get<IAnalyticItem[]>('/api/v1/analytic/order_amount');

	return res.data;
};

export const getAnalyticOrderTotalSum = async () => {
	const res = await api.get<IAnalyticItem[]>('/api/v1/analytic/order_total_sum');

	return res.data;
};

export const getAnalyticOrderAmountProduct = async () => {
	const res = await api.get<IAnalyticItem[]>('/api/v1/analytic/order_amount_product');

	return res.data;
};

export const getAnalyticOrderProductPercentSales = async () => {
	const res = await api.get<{
		telephone_title: string;
		total_sold: number;
	}[]>('/api/v1/analytic/product_percent_sells');

	return res.data;
};

// new
export const getAnalyticBestSellingTelephone = async () => {
	const res = await api.get<{
		title: string;
		total_sells: number;
	}[]>('/api/v1/analytic/best_selling_telephone');

	return res.data;
};

export const getAnalyticMoreThanInWishList = async () => {
	const res = await api.get<{
		title: string;
		quantity_added: number;
	}[]>('/api/v1/analytic/more_than_in_wish_list');

	return res.data;
};

export const getAnalyticVendorsByTelephonesBrand = async (brand: string) => {
	const res = await api.get<{
		id: number;
		first_name: string;
		second_name: string;
		surname: string;
		number_telephone: string;
	}[]>('/api/v1/analytic/vendors_by_telephones_brand', {
		params: {
			brand,
		},
	});

	return res.data;
};

export const getAnalyticUsersPlacedOrderOnDate = async (date: string) => {
	const res = await api.get<{
		username: string;
		first_name: string;
		second_name: string;
	}[]>('/api/v1/analytic/users_placed_order_on_date', {
		params: {
			date,
		},
	});

	return res.data;
};

export const getAnalyticUsersByQuantityAndTotalCostOrder = async () => {
	const res = await api.get<{
		id: number;
		first_name: string;
		second_name: string;
		last_name: string;
		quantity_orders: number;
		total_cost: number;
	}[]>('/api/v1/analytic/users_by_quantity_and_total_cost_order');

	return res.data;
};
