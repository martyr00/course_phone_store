import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { selectCartItems } from '../ducks/cart';
import { EnumLocalStorageKey } from '../utils/types';

const CartProvider = () => {
	const cartItems = useSelector(selectCartItems);

	useEffect(() => {
		localStorage.setItem(
			EnumLocalStorageKey.cartItems,
			JSON.stringify(cartItems),
		);
	}, [JSON.stringify(cartItems)]);

	return null;
};

export default CartProvider;