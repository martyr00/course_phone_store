import { IRegistrationData } from '../utils/types';
import api from '../utils/api';

export const registrationRequest = async (data: IRegistrationData) => {
	const res = await api.post<{
		tokens: {
			access: string,
			refresh: string
		},
	}>('/api/v1/registration', data);

	return res.data;
};

export const loginRequest = async (data: {
	username: string,
	password: string
}) => {
	const res = await api.post<{
		access: string,
		refresh: string
	}>('/api/v1/token', data);

	return res.data;
};