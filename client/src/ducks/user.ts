import { AnyAction } from 'redux';
import { ActionCreatorsFactory, ReducerFactory } from '../utils/helpersRedux';
import { IStore } from '../store';
import { EnumLocalStorageKey, IUser } from '../utils/types';

export interface IState {
	user: IUser | null;
	loaded: boolean;
}

interface IActions {
	logout: () => AnyAction;
	setUser: (payload: IUser | null) => AnyAction;
}

const initialState: IState = {
	user: null,
	loaded: false,
};

export const selectUserData = (state: IStore) => state.user.user;
export const selectUserLoaded = (state: IStore) => state.user.loaded;

export const actionsUser = ActionCreatorsFactory<IActions>(
	{ moduleName: 'user' },
	{
		logout(): IState {
			localStorage.removeItem(EnumLocalStorageKey.accessToken);
			localStorage.removeItem(EnumLocalStorageKey.refreshToken);

			return { user: null, loaded: true };
		},
		setUser: (state, payload): IState => ({
			...state,
			user: payload,
			loaded: true,
		}),
	},
);

export default ReducerFactory(initialState, actionsUser);