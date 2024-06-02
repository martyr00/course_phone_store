import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { Grid } from '@mui/material';
import { useSelector } from 'react-redux';
import { IShortProduct } from '../utils/types';
import { getProductList } from '../service/product';
import { prepareShortProduct } from '../utils/constants';
import ProductListItem from '../components/ProductListItem';
import { selectCompareIds } from '../ducks/compare';

const Compare = () => {
	const [products, setProducts] = useState<IShortProduct[]>([]);

	const compareIds = useSelector(selectCompareIds);

	useEffect(() => {
		getProductList()
			.then((response) => setProducts(response.map(prepareShortProduct)))
			.catch(() => null);
	}, []);

	useEffect(() => {
		setProducts((prev) => prev
			.filter((product) => compareIds.includes(product.id)));
	}, [compareIds.length, products.length]);

	return (
		<Box my={3}>
			<Typography variant="h3" component="h1" my={3}>
				Список порівняння
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

export default Compare;