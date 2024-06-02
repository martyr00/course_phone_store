import React, { useEffect, useState } from 'react';
import {
	TextField,
	Button,
	Container,
	Grid,
	Typography,
	Paper,
	FormControlLabel,
	Switch,
} from '@mui/material';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { IUser } from '../../utils/types';
import { editAdminUserById, getAdminUserById } from '../../service/user';

const UserEdit = () => {
	const [formValues, setFormValues] = useState<IUser | null>(null);

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
		getAdminUserById(id)
			.then(setFormValues)
			.catch(() => null);
	}, [location.pathname]);

	const handleSubmit = () => {
		if (formValues) {
			editAdminUserById(id, formValues)
				.then(() => {
					navigate('/admin/user');
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
					Редагувати користувача
				</Typography>
				<Grid container spacing={3}>
					<Grid item xs={12} sm={6}>
						<TextField
							required
							id="username"
							name="username"
							label="Ім'я користувача"
							fullWidth
							value={formValues.username}
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
							id="date_joined"
							name="date_joined"
							label="Дата приєднання"
							type="date"
							fullWidth
							InputLabelProps={{
								shrink: true,
							}}
							value={formValues.date_joined}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							id="last_login"
							name="last_login"
							label="Останній вхід"
							type="datetime-local"
							fullWidth
							InputLabelProps={{
								shrink: true,
							}}
							value={formValues.last_login || ''}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<TextField
							id="number_telephone"
							name="number_telephone"
							label="Номер телефону"
							fullWidth
							value={formValues.number_telephone || ''}
							onChange={handleChange}
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<FormControlLabel
							control={(
								<Switch
									checked={formValues.is_superuser}
									onChange={handleChange}
									name="is_superuser"
									color="primary"
								/>
							)}
							label="Суперкористувач"
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<FormControlLabel
							control={(
								<Switch
									checked={formValues.is_staff}
									onChange={handleChange}
									name="is_staff"
									color="primary"
								/>
							)}
							label="Персонал"
						/>
					</Grid>
					<Grid item xs={12} sm={6}>
						<FormControlLabel
							control={(
								<Switch
									checked={formValues.is_active}
									onChange={handleChange}
									name="is_active"
									color="primary"
								/>
							)}
							label="Активний"
						/>
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

export default UserEdit;
