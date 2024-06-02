import api from '../utils/api';
import { IVendor } from '../utils/types';

export const getVendorList = async () => {
	const res = await api.get<IVendor[]>('/api/v1/vendor');

	return res.data;
};

export const getVendorItem = async (id: number) => {
	const res = await api.get<IVendor>(`/api/v1/vendor/${id}`);

	return res.data;
};

export const createVendorItem = async (data: IVendor) => {
	const res = await api.post<IVendor>('/api/v1/vendor', data);

	return res.data;
};

export const editVendorItem = async (id: number, data: IVendor) => {
	const res = await api.patch<IVendor>(`/api/v1/vendor/${id}`, data);

	return res.data;
};