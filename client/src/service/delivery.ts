import api from '../utils/api';
import { IDeliveryCreateEdit, IDeliveryItem } from '../utils/types';

export const getDeliveryList = async () => {
	const res = await api.get<IDeliveryItem[]>('/api/v1/delivery');

	return res.data;
};

export const getDeliveryItem = async (id: number) => {
	const res = await api.get<IDeliveryCreateEdit>(`/api/v1/delivery/${id}`);

	return res.data;
};

export const createDeliveryItem = async (data: IDeliveryCreateEdit) => {
	const res = await api.post<IDeliveryCreateEdit>('/api/v1/delivery', data);

	return res.data;
};