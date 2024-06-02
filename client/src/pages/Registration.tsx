import React, { useEffect } from 'react';
import {
	Avatar, Box, Button, Container, Grid, TextField, Typography, Link, Paper,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { actionsUser, selectUserData, selectUserLoaded } from '../ducks/user';
import { registrationRequest } from '../service/auth';
import { EnumLocalStorageKey } from '../utils/types';
import { getSelfUser } from '../service/user';

const Registration: React.FC = () => {
	const userData = useSelector(selectUserData);
	const userLoaded = useSelector(selectUserLoaded);
	const navigate = useNavigate();
	const dispatch = useDispatch();

	useEffect(() => {
		if (userLoaded && userData) {
			navigate('/');
		}
	}, [userLoaded, !!userData]);

	const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
		try {
			event.preventDefault();
			const formData = new FormData(event.currentTarget);

			const res = await registrationRequest({
				password: formData.get('password') as string,
				username: formData.get('username') as string,
				first_name: formData.get('first_name') as string,
				surname: formData.get('surname') as string,
				email: formData.get('email') as string,
				userprofile: {
					number_telephone: formData.get('number_telephone') as string,
					birth_date: formData.get('birth_date') as string,
					second_name: formData.get('second_name') as string,
				},
			});

			localStorage.setItem(EnumLocalStorageKey.accessToken, res.tokens.access);
			localStorage.setItem(EnumLocalStorageKey.refreshToken, res.tokens.refresh);

			const resSelfUser = await getSelfUser();

			dispatch(actionsUser.setUser(resSelfUser));
		} catch (e) {
			// empty error
		}
	};

	return (
		<Container component="main" maxWidth="xs">
			<Paper sx={{ padding: 3, marginTop: 8 }}>
				<Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
					<Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
						<LockOutlinedIcon />
					</Avatar>
					<Typography component="h1" variant="h5">
						Реєстрація
					</Typography>
					<Box component="form" noValidate sx={{ mt: 3 }} onSubmit={handleSubmit}>
						<Grid container spacing={2}>
							<Grid item xs={12}>
								<TextField
									autoComplete="given-name"
									name="first_name"
									required
									fullWidth
									id="firstName"
									label="First Name"
									autoFocus
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									id="surname"
									label="Surname"
									name="surname"
									autoComplete="family-name"
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									id="username"
									label="Username"
									name="username"
									autoComplete="username"
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									id="email"
									label="Email Address"
									name="email"
									autoComplete="email"
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									name="password"
									label="Password"
									type="password"
									id="password"
									autoComplete="new-password"
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									id="number_telephone"
									label="Phone number"
									name="number_telephone"
									autoComplete="phone"
								/>
							</Grid>
							<Grid item xs={12}>
								<TextField
									required
									fullWidth
									id="birth_date"
									label="Birth date"
									name="birth_date"
									autoComplete="bday"
									type="date"
								/>
							</Grid>
						</Grid>
						<Button
							type="submit"
							fullWidth
							variant="contained"
							sx={{ mt: 3, mb: 2 }}
						>
							Реєстрація
						</Button>
						<Grid container justifyContent="flex-end">
							<Grid item>
								<Link component={RouterLink} to="/login" variant="body2">
									Вже є аккаунт? Вхід
								</Link>
							</Grid>
						</Grid>
					</Box>
				</Box>
			</Paper>
		</Container>
	);
};

export default Registration;
