import axios from 'axios';
import { EnumLocalStorageKey } from './types';
import store from '../store';
import { actionsUser } from '../ducks/user';

export const api = axios.create({
	baseURL: process.env.REACT_APP_API_URL,
});

const getRefreshToken = () => (
	axios.post(
		`${process.env.REACT_APP_API_URL}/api/v1/token/refresh`,
		{
			refresh: localStorage.getItem(EnumLocalStorageKey.refreshToken),
		},
	)
		.then(({ data }: { data: { access: string; }}) => {
			localStorage.setItem(EnumLocalStorageKey.accessToken, data.access);

			return Promise.resolve();
		})
		.catch(() => {
			localStorage.removeItem(EnumLocalStorageKey.accessToken);
			localStorage.removeItem(EnumLocalStorageKey.refreshToken);
			store.dispatch(actionsUser.setUser(null));
			window.location.href = '/';

			return Promise.reject(new Error('Unauthenticated'));
		})
);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
api.interceptors.request.use((config: any) => {
	const additionalConfigs = {};
	const token = localStorage.getItem(EnumLocalStorageKey.accessToken);

	if (token) {
		// @ts-ignore
		additionalConfigs.headers = {
			...config.headers,
			Authorization: `Bearer ${token}`,
		};
	}

	return {
		...config,
		...additionalConfigs,
	};
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
}, (error: any) => Promise.reject(error));

// eslint-disable-next-line @typescript-eslint/no-explicit-any
api.interceptors.response.use((response: any) => response, (error: any) => {
	const status = error.response ? error.response.status : null;

	const unauthorizedStatusCode = 401;

	if (status === unauthorizedStatusCode) {
		return getRefreshToken()
			.then(() => {
				const localConfig = { ...error.config };

				localConfig.headers.Authorization = `Bearer ${localStorage.getItem(EnumLocalStorageKey.accessToken)}`;

				return axios.request(localConfig);
			})
			.catch(() => {
				localStorage.removeItem(EnumLocalStorageKey.accessToken);
				localStorage.removeItem(EnumLocalStorageKey.refreshToken);
				store.dispatch(actionsUser.setUser(null));
				window.location.href = '/';

				return Promise.reject(new Error('Unauthenticated'));
			});
	}

	return Promise.reject(error.response);
});

export default api;