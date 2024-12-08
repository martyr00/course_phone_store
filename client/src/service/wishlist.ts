import api from '../utils/api';

export const getWishList = async () => {
	const res = await api.get<{ telephone_id: number }[]>('/api/v1/wish_list');

	return res.data;
};

export const setToWishList = async (id: number) => {
	await api.post(`/api/v1/wish_list/${id}`);
};

export const removeFromWishList = async (id: number) => {
	await api.delete(`/api/v1/wish_list/${id}`);
};