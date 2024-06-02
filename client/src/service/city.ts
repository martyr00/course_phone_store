import api from '../utils/api';
import { ICity } from '../utils/types';

export const getCityList = async () => {
	const res = await api.get<ICity[]>('/api/v1/city');

	return res.data;
};