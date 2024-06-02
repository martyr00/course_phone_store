import React, { useEffect, useState } from 'react';
import {
	TextField,
	Button,
	Container,
	Grid,
	Typography,
	Paper,
	InputLabel,
	Select,
	MenuItem,
	FormControl,
	TableHead,
	TableRow,
	TableCell,
	TableBody,
	Table,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { ICreateOrder, ICity, IShortProduct } from '../utils/types';
import { actionsCart, selectCartItems } from '../ducks/cart';
import { createOrder } from '../service/order';
import { getCityList } from '../service/city';
import { selectUserData } from '../ducks/user';
import { getProductList } from '../service/product';
import { formatterCurrency } from '../utils/constants';

const initialData: ICreateOrder = {
	first_name: '',
	second_name: '',
	surname: '',
	email: '',
	number_telephone: '',
	address: {
		street_name: '',
		city_id: 0,
		post_code: '',
	},
	products: [],
};

const Checkout = () => {
	const [formValues, setFormValues] = useState<ICreateOrder>(initialData);
	const [cityList, setCityList] = useState<ICity[]>([]);
	const [products, setProducts] = useState<IShortProduct[]>([]);
	const cartItems = useSelector(selectCartItems);
	const user = useSelector(selectUserData);
	const navigate = useNavigate();
	const dispatch = useDispatch();

	useEffect(() => {
		getCityList()
			.then(setCityList)
			.catch(() => null);
	}, []);

	useEffect(() => {
		if (cartItems.length < 1) {
			navigate('/');
		} else {
			getProductList()
				.then(setProducts)
				.catch(() => null);

			setFormValues((prevValues) => ({
				...prevValues,
				products: cartItems.map((item) => ({
					telephone_id: item.id,
					amount: item.quantity,
				})),
			}));
		}
	}, [cartItems.length]);

	const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = event.target;
		const keys = name.split('.');
		if (keys.length > 1) {
			setFormValues((prevValues) => ({
				...prevValues,
				address: { ...prevValues.address, [keys[1]]: value },
			}));
		} else {
			setFormValues({ ...formValues, [name]: value });
		}
	};

	const handleSubmit = () => {
		createOrder(formValues)
			.then(() => {
				setFormValues(initialData);
				dispatch(actionsCart.clearCart());
				navigate('/');
			})
			.catch(() => null);
	};

	return (
		<Container sx={{ margin: '40px auto' }}>
			<Paper style={{ padding: 16 }}>
				<Typography variant="h6" gutterBottom>
					Оформлення замовлення
				</Typography>
				<Grid container spacing={3}>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="first_name"
							name="first_name"
							label="Ім'я"
							fullWidth
							value={formValues.first_name}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="second_name"
							name="second_name"
							label="По-батькові"
							fullWidth
							value={formValues.second_name}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="surname"
							name="surname"
							label="Прізвище"
							fullWidth
							value={formValues.surname}
							onChange={handleChange}
						/>
					</Grid>
					{!user ? (
						<>
							<Grid item xs={12} sm={6}>
								<TextField
									required
									id="email"
									name="email"
									label="Електронна пошта"
									type="email"
									fullWidth
									value={formValues.email}
									onChange={handleChange}
								/>
							</Grid>
							<Grid item xs={12} sm={6}>
								<TextField
									required
									id="number_telephone"
									name="number_telephone"
									label="Номер телефону"
									fullWidth
									value={formValues.number_telephone}
									onChange={handleChange}
								/>
							</Grid>
						</>
					) : null}
					<Grid item xs={12}>
						<Typography variant="h6" gutterBottom>
							Адреса
						</Typography>
					</Grid>
					<Grid item xs={12} sm={6}>
						<FormControl fullWidth>
							<InputLabel id="select-label-city">Місто</InputLabel>
							<Select
								labelId="select-label-city"
								value={formValues.address.city_id}
								label="Місто"
								fullWidth
								onChange={(e) => {
									setFormValues({
										...formValues,
										address: {
											...formValues.address,
											city_id: e.target.value as number,
										},
									});
								}}
							>
								{cityList.map((option) => (
									<MenuItem key={option.id} value={option.id}>
										{option.name}
									</MenuItem>
								))}
							</Select>
						</FormControl>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="address.street_name"
							name="address.street_name"
							label="Вулиця"
							fullWidth
							value={formValues.address.street_name}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="address.post_code"
							name="address.post_code"
							label="Поштовий індекс"
							fullWidth
							value={formValues.address.post_code}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12}>
						<Typography variant="h6" gutterBottom>
							Телефони
						</Typography>

						<Table>
							<TableHead>
								<TableRow sx={{ whiteSpace: 'nowrap', fontWeight: 600 }}>
									<TableCell>Назва</TableCell>
									<TableCell>Ціна</TableCell>
									<TableCell>Кількість</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{formValues.products.map((item) => (
									<TableRow key={item.telephone_id}>
										<TableCell>
											{products.find((i) => i.id === item.telephone_id)?.title || ''}
										</TableCell>
										<TableCell>
											{formatterCurrency.format(
												products.find((i) => i.id === item.telephone_id)?.price || 0,
											)}
										</TableCell>
										<TableCell>
											<TextField
												required
												id={`amount-${item.telephone_id}`}
												name="amount"
												label="Кількість"
												type="number"
												fullWidth
												value={item.amount}
												onChange={(e) => {
													setFormValues(() => ({
														...formValues,
														products: formValues.products.map((product) => (
															product.telephone_id === item.telephone_id
																? { ...product, amount: parseInt(e.target.value, 10) || 0 }
																: product
														)),
													}));
												}}
											/>
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</Grid>
					<Grid item xs={12}>
						<Button
							variant="contained"
							color="primary"
							onClick={handleSubmit}
						>
							Оформити замовлення
						</Button>
					</Grid>
				</Grid>
			</Paper>
		</Container>
	);
};

export default Checkout;