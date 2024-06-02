import { AnyAction } from 'redux';
import { ActionCreatorsFactory, ReducerFactory } from '../utils/helpersRedux';
import { EnumLocalStorageKey } from '../utils/types';
import { IStore } from '../store';

export interface ICartItem {
	id: number;
	quantity: number;
}

const getCartItemsLS = () => {
	try {
		return 	localStorage.getItem(EnumLocalStorageKey.cartItems) !== null
			? JSON.parse(<string>localStorage.getItem(EnumLocalStorageKey.cartItems))
			: [];
	} catch (e) {
		return [];
	}
};

export interface IState {
	items: ICartItem[];
}

const initialState: IState = {
	items: getCartItemsLS(),
};

interface IActions {
	setCartItems: (payload: ICartItem[]) => AnyAction;
	increaseCartQuantity: (productId: number) => AnyAction;
	decrementCartQuantity: (productId: number) => AnyAction;
	removeItem: (productId: number) => AnyAction;
	clearCart: () => AnyAction;
}

export const selectCartItems = (state: IStore) => state.cart.items;

export const actionsCart = ActionCreatorsFactory<IActions>(
	{ moduleName: 'cart' },
	{
		setCartItems(state: IState, payload: ICartItem[]): IState {
			return ({
				...state,
				items: payload,
			});
		},

		increaseCartQuantity(state: IState, payload: number): IState {
			const id = payload;
			const existingItem = state.items.find((item) => item.id === id);
			if (existingItem) {
				return {
					...state,
					items: state.items.map((item) => (item.id === id ? {
						...item,
						quantity: item.quantity + 1,
					} : item)),
				};
			}
			return ({
				...state,
				items: [
					...state.items,
					{
						id: payload,
						quantity: 1,
					},
				],
			});
		},

		decrementCartQuantity(state: IState, payload: number): IState {
			const id = payload;
			return {
				...state,
				items: state.items.map((item) => (item.id === id ? ({
					...item,
					quantity: item.quantity - 1,
				}) : item)).filter((item) => item.quantity > 0),
			};
		},

		removeItem(state: IState, payload: number): IState {
			const id = payload;
			const updatedCartItems = state.items.filter((card) => card.id !== id);

			return {
				...state,
				items: updatedCartItems,
			};
		},

		clearCart(): IState {
			localStorage.removeItem(EnumLocalStorageKey.cartItems);

			return {
				items: [],
			};
		},
	},
);

export default ReducerFactory(initialState, actionsCart);