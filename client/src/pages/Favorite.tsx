import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { Grid } from '@mui/material';
import { useSelector } from 'react-redux';
import { IShortProduct } from '../utils/types';
import { getProductList } from '../service/product';
import { prepareShortProduct } from '../utils/constants';
import ProductListItem from '../components/ProductListItem';
import { selectFavoriteIds } from '../ducks/favorite';

const Favorite = () => {
	const [products, setProducts] = useState<IShortProduct[]>([]);

	const favoriteIds = useSelector(selectFavoriteIds);

	useEffect(() => {
		getProductList()
			.then((response) => setProducts(response.map(prepareShortProduct)))
			.catch(() => null);
	}, []);

	useEffect(() => {
		setProducts((prev) => prev
			.filter((product) => favoriteIds.includes(product.id)));
	}, [favoriteIds.length, products.length]);

	return (
		<Box my={3}>
			<Typography variant="h3" component="h1" my={3}>
				Список обраного
			</Typography>
			<Grid container my={2}>
				{products.map((product) => (
					<ProductListItem
						key={product.id}
						{...product}
					/>
				))}
			</Grid>
		</Box>
	);
};

export default Favorite;