import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { EnumLocalStorageKey } from '../utils/types';
import { getSelfUser } from '../service/user';
import { actionsUser } from '../ducks/user';

const UserProvider = () => {
	const dispatch = useDispatch();

	const initDataFromServer = async () => {
		try {
			if (localStorage.getItem(EnumLocalStorageKey.accessToken)) {
				const data = await getSelfUser();

				dispatch(actionsUser.setUser(data));
			} else {
				dispatch(actionsUser.setUser(null));
			}
		} catch (e) {
			dispatch(actionsUser.setUser(null));
		}
	};

	useEffect(() => {
		initDataFromServer();
	}, []);

	return null;
};

export default UserProvider;