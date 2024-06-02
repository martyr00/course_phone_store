import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import {
	Button,
	Container,
	FormControl,
	Grid,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableRow,
	TextField,
	Typography,
} from '@mui/material';
import { IOrderItem, IShortProduct } from '../../utils/types';
import { editOrderItem, getOrderItem } from '../../service/order';
import { formatterCurrency } from '../../utils/constants';
import { getProductList } from '../../service/product';

const OrdersEdit = () => {
	const [formValues, setFormValues] = useState<IOrderItem | null>(null);
	const [products, setProducts] = useState<IShortProduct[]>([]);

	const location = useLocation();
	const { id: idFromUrl } = useParams();
	const navigate = useNavigate();

	const id = parseInt((idFromUrl || ''), 10);

	const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = event.target;

		if (formValues) {
			setFormValues({ ...formValues, [name]: value });
		}
	};

	useEffect(() => {
		getOrderItem(id)
			.then(setFormValues)
			.catch(() => null);
	}, [location.pathname]);

	useEffect(() => {
		getProductList()
			.then(setProducts)
			.catch(() => null);
	}, []);

	const handleSubmit = () => {
		if (formValues) {
			editOrderItem(id, formValues)
				.then(() => {
					navigate('/admin/order');
				})
				.catch(() => null);
		}
	};

	if (!formValues) {
		return null;
	}

	return (
		<Container>
			<Paper style={{ padding: 16 }}>
				<Typography variant="h6" gutterBottom>
					Редагувати замовлення
				</Typography>
				<Grid container spacing={3}>
					<Grid item xs={12} sm={6}>
						<FormControl fullWidth>
							<InputLabel id="select-label-brand">Статус</InputLabel>
							<Select
								labelId="select-label-brand"
								value={formValues.status}
								label="Статус"
								fullWidth
								onChange={(e) => {
									setFormValues({ ...formValues, status: e.target.value });
								}}
							>
								<MenuItem value="PENDING">Очікування</MenuItem>
								<MenuItem value="PREPARATION">Обробка</MenuItem>
								<MenuItem value="SENDED">Відправка</MenuItem>
								<MenuItem value="DONE">Виконано</MenuItem>
								<MenuItem value="CANCELED">Відхилено</MenuItem>
							</Select>
						</FormControl>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="user_id"
							name="user_id"
							label="ID користувача"
							type="number"
							fullWidth
							value={formValues.user_id}
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
							id="street"
							name="street"
							label="Вулиця"
							fullWidth
							value={formValues.street}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="post_code"
							name="post_code"
							label="Поштовий індекс"
							fullWidth
							value={formValues.post_code}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="full_price"
							name="full_price"
							label="Повна ціна"
							type="number"
							fullWidth
							value={formValues.full_price}
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
								{formValues.order_product_details.map((item) => (
									<TableRow key={item.telephone_id}>
										<TableCell>
											{products.find((i) => i.id === item.telephone_id)?.title || ''}
										</TableCell>
										<TableCell>
											{formatterCurrency.format(item.price)}
										</TableCell>
										<TableCell>
											{item.amount}
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
							Зберегти
						</Button>
					</Grid>
				</Grid>
			</Paper>
		</Container>
	);
};

export default OrdersEdit;