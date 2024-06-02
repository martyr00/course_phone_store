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