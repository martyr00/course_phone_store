import React from 'react';
import UserProvider from './UserProvider';
import FavoriteProvider from './FavoriteProvider';
import CartProvider from './CartProvider';
import CompareProvider from './CompareProvider';

interface IProps {
	children: React.ReactNode;
}

const CustomProviders = ({ children }: IProps) => (
	<>
		<UserProvider />
		<FavoriteProvider />
		<CartProvider />
		<CompareProvider />
		{children}
	</>
);

export default CustomProviders;