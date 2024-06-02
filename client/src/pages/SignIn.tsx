import React, { useEffect, useState } from 'react';
import {
	Avatar,
	Box,
	Button,
	Container,
	Grid,
	Link,
	Paper,
	TextField,
	Typography,
	InputAdornment,
	IconButton,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { actionsUser, selectUserData, selectUserLoaded } from '../ducks/user';
import { loginRequest } from '../service/auth';
import { EnumLocalStorageKey } from '../utils/types';
import { getSelfUser } from '../service/user';

const SignIn = () => {
	const [showPassword, setShowPassword] = useState(false);

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

			const resLoginRequest = await loginRequest({
				username: formData.get('username') as string,
				password: formData.get('password') as string,
			});

			localStorage.setItem(EnumLocalStorageKey.accessToken, resLoginRequest.access);
			localStorage.setItem(EnumLocalStorageKey.refreshToken, resLoginRequest.refresh);

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
						Вхід
					</Typography>
					<Box component="form" noValidate sx={{ mt: 3 }} onSubmit={handleSubmit}>
						<TextField
							margin="normal"
							fullWidth
							required
							id="username"
							label="Username"
							name="username"
							aria-required
							autoComplete="username"
							autoFocus
						/>
						<TextField
							margin="normal"
							required
							fullWidth
							name="password"
							label="Password"
							type={showPassword ? 'text' : 'password'}
							id="password"
							InputProps={{
								endAdornment: (
									<InputAdornment position="end">
										<IconButton
											aria-label="toggle password visibility"
											onClick={() => setShowPassword(!showPassword)}
											edge="end"
										>
											{showPassword ? <VisibilityOff /> : <Visibility />}
										</IconButton>
									</InputAdornment>
								),
							}}
							autoComplete="current-password"
						/>
						<Button
							type="submit"
							fullWidth
							variant="contained"
							sx={{ mt: 3, mb: 2 }}
						>
							Вхід
						</Button>
						<Grid container>
							<Grid item>
								<Link component={RouterLink} to="/registration" variant="body2">
									Відсутній аккаунт? Зареєструватися
								</Link>
							</Grid>
						</Grid>
					</Box>
				</Box>
			</Paper>
		</Container>
	);
};

export default SignIn;
