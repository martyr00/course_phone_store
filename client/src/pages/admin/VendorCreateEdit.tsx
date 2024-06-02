import React, { useEffect, useState } from 'react';
import {
	TextField,
	Button,
	Container,
	Grid,
	Typography,
	Paper,
} from '@mui/material';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { IVendor } from '../../utils/types';
import { createVendorItem, editVendorItem, getVendorItem } from '../../service/vendor';

const initialProduct: IVendor = {
	first_name: '',
	second_name: '',
	surname: '',
	number_telephone: '',
};

const VendorForm = () => {
	const [formValues, setFormValues] = useState<IVendor>(initialProduct);

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
			getVendorItem(parseInt(idFromUrl, 10))
				.then(setFormValues)
				.catch(() => null);
		}
	}, [location.pathname]);

	const handleSubmit = () => {
		if (isEdit) {
			editVendorItem(parseInt(idFromUrl, 10), formValues)
				.then(() => {
					navigate('/admin/vendor');
				})
				.catch(() => null);
		} else {
			createVendorItem(formValues)
				.then(() => {
					navigate('/admin/vendor');
				})
				.catch(() => null);
		}
	};

	return (
		<Container>
			<Paper style={{ padding: 16 }}>
				<Typography variant="h6" gutterBottom>
					{isEdit ? 'Редагувати постачальника' : 'Створити постачальника'}
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

export default VendorForm;
