import api from '../utils/api';
import { IBrand } from '../utils/types';

export const getBrandList = async () => {
	const res = await api.get<IBrand[]>('/api/v1/brand');

	return res.data;
};