import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Badge from '@mui/material/Badge';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import { Link as RouterLink } from 'react-router-dom';
import Link from '@mui/material/Link';
import Box from '@mui/material/Box';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import { useDispatch, useSelector } from 'react-redux';
import { actionsUser, selectUserData } from '../ducks/user';
import { EnumLocalStorageKey } from '../utils/types';
import { selectCompareIds } from '../ducks/compare';
import { selectFavoriteIds } from '../ducks/favorite';
import { selectCartItems } from '../ducks/cart';

const Header: React.FC = () => {
	const [drawerOpen, setDrawerOpen] = useState(false);
	const theme = useTheme();
	const isMobile = useMediaQuery(theme.breakpoints.down('md'));

	const user = useSelector(selectUserData);

	const compareIds = useSelector(selectCompareIds);
	const favoriteIds = useSelector(selectFavoriteIds);
	const cartIds = useSelector(selectCartItems);

	const dispatch = useDispatch();

	const toggleDrawer = (open: boolean) => () => {
		setDrawerOpen(open);
	};

	const menuItems: {
		text: string;
		to: string;
		badge?: number;
		onClick?: () => void;
	}[] = [
		{ text: 'Порівняння', to: '/compare', badge: compareIds.length },
		{ text: 'Обране', to: '/favorite', badge: favoriteIds.length },
		{ text: 'Кошик', to: '/checkout', badge: cartIds.length },
	];

	if (user?.is_superuser) {
		menuItems.push({ text: 'Адмін Панель', to: '/admin' });
	}

	if (user) {
		menuItems.push({
			text: 'Вихід',
			to: '/',
			onClick() {
				localStorage.removeItem(EnumLocalStorageKey.accessToken);
				localStorage.removeItem(EnumLocalStorageKey.refreshToken);

				dispatch(actionsUser.setUser(null));
			},
		});
	} else {
		menuItems.push({ text: 'Вхід', to: '/login' });
		menuItems.push({ text: 'Реєстрація', to: '/registration' });
	}

	return (
		<AppBar position="static">
			<Container maxWidth="xl">
				<Toolbar>
					<Typography variant="h6" sx={{ flexGrow: 1 }}>
						<Link component={RouterLink} to="/" color="inherit" underline="none">
							My Store
						</Link>
					</Typography>
					{isMobile ? (
						<>
							<IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
								<MenuIcon />
							</IconButton>
							<Drawer anchor="right" open={drawerOpen} onClose={toggleDrawer(false)}>
								<List>
									{menuItems.map((item) => (
										<ListItem
											key={item.text}
											button
											component={RouterLink}
											to={item.to}
											onClick={() => {
												toggleDrawer(false);

												if (item.onClick) item.onClick();
											}}
										>
											<Badge color="secondary" badgeContent={item.badge}>
												<ListItemText primary={item.text} />
											</Badge>
										</ListItem>
									))}
								</List>
							</Drawer>
						</>
					) : (
						<Box sx={{ display: 'flex', gap: 2 }}>
							{menuItems.map((item) => (
								<Badge key={item.text} color="secondary" badgeContent={item.badge}>
									<Link
										component={RouterLink}
										to={item.to}
										color="inherit"
										underline="none"
										key={item.text}
										onClick={item.onClick}
									>
										<Button color="inherit">{item.text}</Button>
									</Link>
								</Badge>
							))}
						</Box>
					)}
				</Toolbar>
			</Container>
		</AppBar>
	);
};

export default Header;
