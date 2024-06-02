import api from '../utils/api';
import { ICreateOrder, IOrder, IOrderItem } from '../utils/types';

export const getOrderList = async () => {
	const res = await api.get<IOrder[]>('/api/v1/admin/order');

	return res.data;
};

export const getOrderItem = async (id: number) => {
	const res = await api.get<IOrderItem>(`/api/v1/order/${id}`);

	return res.data;
};

export const createOrder = async (data: ICreateOrder) => {
	const res = await api.post<IOrder>('/api/v1/order', data);

	return res.data;
};

export const editOrderItem = async (id: number, data: IOrder) => {
	const res = await api.patch<IOrder>(`/api/v1/order/${id}`, data);

	return res.data;
};