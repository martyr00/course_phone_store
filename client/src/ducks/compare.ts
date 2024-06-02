import { AnyAction } from 'redux';
import { ActionCreatorsFactory, ReducerFactory } from '../utils/helpersRedux';
import { IStore } from '../store';
import { EnumLocalStorageKey } from '../utils/types';

const getInitialItems = () => {
	try {
		const savedData = localStorage.getItem(EnumLocalStorageKey.compareItems);

		if (savedData) return JSON.parse(savedData);
	} catch (e) {
		// empty block
	}

	return [];
};

export interface IState {
	items: number[],
}

const initialState: IState = {
	items: getInitialItems(),
};

interface IActions {
	toggleProduct: (productId: number) => AnyAction;
}

export const selectCompareIds = (state: IStore) => state.compare.items;

export const actionsCompare = ActionCreatorsFactory<IActions>(
	{ moduleName: 'compare' },
	{
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

export default ReducerFactory(initialState, actionsCompare);