import React, { useEffect, useState } from 'react';
import {
	Grid,
	Select,
	FormControl,
	InputLabel,
	MenuItem,
} from '@mui/material';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useLocation, useNavigate } from 'react-router-dom';
import { IShortProduct } from '../utils/types';
import { getProductList } from '../service/product';
import ProductListItem from '../components/ProductListItem';
import { prepareShortProduct } from '../utils/constants';

type TSortKey = 'title|asc' | 'title|desc' | 'price|asc' | 'price|desc';

const sortingOptions: { key: TSortKey, label: string }[] = [
	{
		key: 'title|asc',
		label: 'Назва: за зростанням',
	},
	{
		key: 'title|desc',
		label: 'Назва: за спаданням',
	},
	{
		key: 'price|asc',
		label: 'Ціна: за зростанням',
	},
	{
		key: 'price|desc',
		label: 'Ціна: за спаданням',
	},
];

const Catalog = () => {
	const [products, setProducts] = useState<IShortProduct[]>([]);
	const [sorting, setSorting] = useState<TSortKey>('title|asc');

	const location = useLocation();
	const navigate = useNavigate();

	useEffect(() => {
		const searchParams = new URLSearchParams(location.search);

		if (searchParams.has('sort')) {
			const sortValue = searchParams.get('sort') as TSortKey;
			setSorting(sortValue);
		}
	}, [location.search]);

	const handleChangeSorting = (val: TSortKey) => {
		const searchParams = new URLSearchParams(location.search);

		if (searchParams.has('sort')) {
			searchParams.delete('sort');
		}

		searchParams.append('sort', val);

		navigate({ search: searchParams.toString() });
	};

	useEffect(() => {
		const searchParams = new URLSearchParams(location.search);

		const params: Record<string, string | number> = {};

		if (searchParams.has('sort')) {
			const sort = searchParams.get('sort');

			params.sort_by = sort?.split('|')[0] || 'title';
			params.sort_dir = sort?.split('|')[1] || 'asc';
		}

		getProductList(params)
			.then((response) => setProducts(response.map(prepareShortProduct)))
			.catch(() => null);
	}, [location.search]);

	return (
		<Box my={3}>
			<Typography variant="h3" component="h1" my={3}>
				Каталог товарів
			</Typography>
			<Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
				<FormControl>
					<InputLabel id="sorting-select-label">Сортування</InputLabel>
					<Select
						labelId="sorting-select-label"
						value={sorting}
						label="Сортування"
						onChange={(e) => handleChangeSorting(e.target.value as TSortKey)}
					>
						{sortingOptions.map((option) => (
							<MenuItem key={option.key} value={option.key}>
								{option.label}
							</MenuItem>
						))}
					</Select>
				</FormControl>
			</Box>
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

export default Catalog;