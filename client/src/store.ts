import { createStore, combineReducers } from 'redux';
import cart, { IState as IStateCart } from './ducks/cart';
import compare, { IState as IStateCompare } from './ducks/compare';
import favorite, { IState as IStateFavorite } from './ducks/favorite';
import user, { IState as IStateUser } from './ducks/user';

export interface IStore {
	user: IStateUser;
	cart: IStateCart;
	compare: IStateCompare;
	favorite: IStateFavorite;
}

const store = createStore(
	combineReducers({
		cart,
		compare,
		favorite,
		user,
	}),
);

export default store;