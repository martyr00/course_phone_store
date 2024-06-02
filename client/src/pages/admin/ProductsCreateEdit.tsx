import React, { useEffect, useState } from 'react';
import {
	TextField,
	Button,
	Container,
	Grid,
	Typography,
	Paper, InputLabel, Select, MenuItem, FormControl,
} from '@mui/material';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { IBrand, IDetailProduct } from '../../utils/types';
import { createProductItem, editProductItem, getProductItem } from '../../service/product';
import { getBrandList } from '../../service/brand';

const initialProduct: IDetailProduct = {
	id: 0,
	brand: '',
	images: [],
	title: '',
	price: 0,
	brand_id: 0,
	description: '',
	diagonal_screen: 0,
	built_in_memory: '',
	weight: 0,
	number_stock: 0,
	discount: 0,
	release_date: '',
};

const ProductForm = () => {
	const [formValues, setFormValues] = useState<IDetailProduct>(initialProduct);

	const [brandList, setBrandList] = useState<IBrand[]>([]);

	const location = useLocation();
	const { id: idFromUrl } = useParams();
	const navigate = useNavigate();

	const isEdit = !!idFromUrl;

	const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = event.target;
		setFormValues({ ...formValues, [name]: value });
	};

	useEffect(() => {
		setFormValues(initialProduct);

		if (isEdit) {
			getProductItem(parseInt(idFromUrl, 10))
				.then(setFormValues)
				.catch(() => null);
		}
	}, [location.pathname]);

	useEffect(() => {
		getBrandList()
			.then(setBrandList)
			.catch(() => null);
	}, []);

	const handleSubmit = () => {
		if (isEdit) {
			editProductItem(parseInt(idFromUrl, 10), formValues)
				.then(() => {
					navigate('/admin/product');
				})
				.catch(() => null);
		} else {
			createProductItem(formValues)
				.then(() => {
					navigate('/admin/product');
				})
				.catch(() => null);
		}
	};

	return (
		<Container>
			<Paper style={{ padding: 16 }}>
				<Typography variant="h6" gutterBottom>
					{isEdit ? 'Редагувати товар' : 'Створити товар'}
				</Typography>
				<Grid container spacing={3}>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="title"
							name="title"
							label="Назва"
							fullWidth
							value={formValues.title}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="price"
							name="price"
							label="Ціна"
							type="number"
							fullWidth
							value={formValues.price}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<FormControl fullWidth>
							<InputLabel id="select-label-brand">Бренд</InputLabel>
							<Select
								labelId="select-label-brand"
								value={formValues.brand_id}
								label="Бренд"
								fullWidth
								onChange={(e) => {
									setFormValues({ ...formValues, brand_id: e.target.value as number });
								}}
							>
								{brandList.map((option) => (
									<MenuItem key={option.id} value={option.id}>
										{option.title}
									</MenuItem>
								))}
							</Select>
						</FormControl>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="diagonal_screen"
							name="diagonal_screen"
							label="Діагональ екрана (дюйми)"
							type="number"
							fullWidth
							value={formValues.diagonal_screen}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="built_in_memory"
							name="built_in_memory"
							label="Вбудована пам'ять"
							fullWidth
							value={formValues.built_in_memory}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="weight"
							name="weight"
							label="Вага (г)"
							type="number"
							fullWidth
							value={formValues.weight}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="discount"
							name="discount"
							label="Знижка (%)"
							type="number"
							fullWidth
							value={formValues.discount}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="release_date"
							name="release_date"
							label="Дата випуску"
							type="date"
							fullWidth
							InputLabelProps={{
								shrink: true,
							}}
							value={formValues.release_date}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12}>
						<TextField
							required
							id="description"
							name="description"
							label="Опис"
							multiline
							rows={4}
							fullWidth
							value={formValues.description}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12}>
						<Button
							variant="contained"
							color="primary"
							onClick={handleSubmit}
						>
							{isEdit ? 'Зберегти' : 'Створити'}
						</Button>
					</Grid>
				</Grid>
			</Paper>
		</Container>
	);
};

export default ProductForm;
