import api from '../utils/api';
import { IDetailProduct, IProductEditCreateData, IShortProduct } from '../utils/types';

export const getProductList = async (params?: Record<string, string | number>) => {
	const res = await api.get<IShortProduct[]>('/api/v1/product', {
		params,
	});

	return res.data;
};

export const getAdminProductList = async () => {
	const res = await api.get<IDetailProduct[]>('/api/v1/product?fulldata=1');

	return res.data;
};

export const getProductItem = async (id: number) => {
	const res = await api.get<IDetailProduct>(`/api/v1/product/${id}`);

	return res.data;
};

export const createProductItem = async (data: IProductEditCreateData) => {
	const res = await api.post<IDetailProduct>('/api/v1/product', data);

	return res.data;
};

export const editProductItem = async (id: number, data: IProductEditCreateData) => {
	const res = await api.patch<IDetailProduct>(`/api/v1/product/${id}`, data);

	return res.data;
};