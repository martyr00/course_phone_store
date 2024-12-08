import { AnyAction } from 'redux';
import { ActionCreatorsFactory, ReducerFactory } from '../utils/helpersRedux';
import { IStore } from '../store';

export interface IState {
	items: number[],
}

const initialState: IState = {
	items: [],
};

interface IActions {
	setItems: (productIds: number[]) => AnyAction;
	toggleProduct: (productId: number) => AnyAction;
}

export const selectFavoriteIds = (state: IStore) => state.favorite.items;

export const actionsFavorite = ActionCreatorsFactory<IActions>(
	{ moduleName: 'favorite' },
	{
		setItems(state: IState, productIds: number[]): IState {
			return ({
				...state,
				items: productIds,
			});
		},
		toggleProduct(state: IState, productId: number): IState {
			if (state.items.some((item) => item === productId)) {
				return ({
					...state,
					items: state.items.filter((item) => item !== productId),
				});
			}

			return ({
				...state,
				items: [...state.items, productId],
			});
		},
	},
);

export default ReducerFactory(initialState, actionsFavorite);