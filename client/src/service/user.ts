import api from '../utils/api';
import { IUser } from '../utils/types';

export const getSelfUser = async () => {
	const res = await api.get<IUser>('/api/v1/user/self');

	return res.data;
};

export const editSelfUser = async (data: IUser) => {
	const res = await api.patch<null>('/api/v1/user/self', data);

	return res.data;
};

export const getAdminUserList = async () => {
	const res = await api.get<IUser[]>('/api/v1/user');

	return res.data;
};

export const getAdminUserById = async (id: number) => {
	const res = await api.get<IUser>(`/api/v1/user/${id}`);

	return res.data;
};

export const editAdminUserById = async (id: number, data: IUser) => {
	const res = await api.patch<null>(`/api/v1/user/${id}`, data);

	return res.data;
};