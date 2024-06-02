import React, { useEffect, useState } from 'react';
import {
	TextField,
	Button,
	Container,
	Grid,
	Typography,
	Paper,
	FormControl,
	InputLabel,
	Select,
	MenuItem,
	Table,
	TableHead,
	TableRow,
	TableCell,
	TableBody,
} from '@mui/material';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { IDeliveryCreateEdit, IShortProduct, IVendor } from '../../utils/types';
import { getVendorList } from '../../service/vendor';
import { createDeliveryItem, getDeliveryItem } from '../../service/delivery';
import { getProductList } from '../../service/product';

const initialProduct: IDeliveryCreateEdit = {
	vendor_id: 0,
	delivery_details: [],
};

const DeliveryForm = () => {
	const [formValues, setFormValues] = useState<IDeliveryCreateEdit>(initialProduct);
	const [products, setProducts] = useState<IShortProduct[]>([]);
	const [vendorList, setVendorList] = useState<IVendor[]>([]);

	const location = useLocation();
	const { id: idFromUrl } = useParams();
	const navigate = useNavigate();

	const isEdit = !!idFromUrl;

	useEffect(() => {
		setFormValues(initialProduct);

		if (isEdit) {
			getDeliveryItem(parseInt(idFromUrl, 10))
				.then(setFormValues)
				.catch(() => null);
		}
	}, [location.pathname]);

	useEffect(() => {
		getVendorList()
			.then(setVendorList)
			.catch(() => null);

		getProductList()
			.then(setProducts)
			.catch(() => null);
	}, []);

	const vendor: IVendor | undefined = vendorList
		.find((item) => item.id === formValues.vendor_id);

	const handleSubmit = () => {
		if (isEdit) {
			navigate('/admin/delivery');
		} else {
			createDeliveryItem(formValues)
				.then(() => {
					navigate('/admin/delivery');
				})
				.catch(() => null);
		}
	};

	return (
		<Container sx={{ margin: '40px auto' }}>
			<Paper style={{ padding: 16 }}>
				<Typography variant="h6" gutterBottom>
					Поставка
				</Typography>
				<Grid container spacing={3}>
					<Grid item xs={12}>
						<FormControl fullWidth>
							<InputLabel id="select-label-vendor">Постачальник</InputLabel>
							<Select
								labelId="select-label-city"
								value={formValues.vendor_id}
								label="Постачальник"
								fullWidth
								disabled={isEdit}
								onChange={(e) => {
									if (!isEdit) {
										setFormValues({
											...formValues,
											vendor_id: e.target.value as number,
										});
									}
								}}
							>
								{vendorList.map((option) => (
									<MenuItem key={option.id} value={option.id}>
										{`${option.first_name} ${option.second_name} ${option.surname}`}
									</MenuItem>
								))}
							</Select>
						</FormControl>
					</Grid>

					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="first_name"
							name="first_name"
							disabled={isEdit}
							label="Ім'я"
							fullWidth
							value={vendor?.first_name || ''}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="second_name"
							name="second_name"
							label="По-батькові"
							disabled={isEdit}
							fullWidth
							value={vendor?.second_name || ''}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="surname"
							name="surname"
							label="Прізвище"
							disabled={isEdit}
							fullWidth
							value={vendor?.surname || ''}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="number_telephone"
							name="number_telephone"
							label="Телефон"
							disabled={isEdit}
							fullWidth
							value={vendor?.number_telephone || ''}
						/>
					</Grid>
					<Grid item xs={12}>
						<Typography variant="h6" gutterBottom>
							Продукти
						</Typography>

						{isEdit ? null : (
							<Button
								variant="contained"
								color="primary"
								onClick={() => {
									setFormValues({
										...formValues,
										delivery_details: [
											{
												telephone_id: 0,
												price_one_phone: 0,
												amount: 0,
											},
											...formValues.delivery_details,
										],
									});
								}}
							>
								Додати продукт
							</Button>
						)}

						<Table>
							<TableHead>
								<TableRow sx={{ whiteSpace: 'nowrap', fontWeight: 600 }}>
									<TableCell>Назва</TableCell>
									<TableCell>Ціна</TableCell>
									<TableCell>Кількість</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{formValues.delivery_details.map((item, index) => (
									// eslint-disable-next-line react/no-array-index-key
									<TableRow key={`${item.telephone_id}_${index}`}>
										<TableCell>
											<FormControl fullWidth>
												<InputLabel id="select-label-product">Телефон</InputLabel>
												<Select
													labelId="select-label-product"
													value={item.telephone_id}
													label="Телефон"
													fullWidth
													disabled={isEdit}
													onChange={(e) => {
														if (!isEdit) {
															setFormValues(() => ({
																...formValues,
																delivery_details: formValues.delivery_details.map((i, idx) => ({
																	...i,
																	// eslint-disable-next-line no-nested-ternary
																	telephone_id: idx === index
																		? (typeof e.target.value === 'string' ? parseInt(e.target.value, 10) : e.target.value)
																		: i.telephone_id,
																})),
															}));
														}
													}}
												>
													{products.map((option) => (
														<MenuItem key={option.id} value={option.id}>
															{option.title}
														</MenuItem>
													))}
												</Select>
											</FormControl>
										</TableCell>
										<TableCell>
											<TextField
												required
												id={`price-${item.telephone_id}`}
												name="price"
												label="Ціна"
												fullWidth
												disabled={isEdit}
												value={item?.price_one_phone}
												onChange={(e) => {
													if (!isEdit) {
														setFormValues(() => ({
															...formValues,
															delivery_details: formValues.delivery_details.map((i, idx) => ({
																...i,
																price_one_phone: idx === index
																	? parseInt(e.target.value, 10)
																	: i.price_one_phone,
															})),
														}));
													}
												}}
											/>
										</TableCell>
										<TableCell>
											<TextField
												required
												id={`amount-${item.telephone_id}`}
												name="amount"
												label="Кількість"
												type="number"
												fullWidth
												disabled={isEdit}
												value={item.amount}
												onChange={(e) => {
													if (!isEdit) {
														setFormValues(() => ({
															...formValues,
															delivery_details: formValues.delivery_details.map((i, idx) => ({
																...i,
																amount: idx === index ? parseInt(e.target.value, 10) : i.amount,
															})),
														}));
													}
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
							{isEdit ? 'Закрити' : 'Створити'}
						</Button>
					</Grid>
				</Grid>
			</Paper>
		</Container>
	);
};

export default DeliveryForm;
