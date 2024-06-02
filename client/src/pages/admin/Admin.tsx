import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';
import {
	Outlet, useLocation, useNavigate, Link,
} from 'react-router-dom';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { Box } from '@mui/material';
import { selectUserData, selectUserLoaded } from '../../ducks/user';

const Admin = () => {
	const userData = useSelector(selectUserData);
	const userLoaded = useSelector(selectUserLoaded);
	const navigate = useNavigate();
	const location = useLocation();

	useEffect(() => {
		if (userLoaded && !userData?.is_superuser) {
			navigate('/404');
		}
	}, [userLoaded, JSON.stringify(userData)]);

	if (userLoaded && !userData?.is_superuser) {
		return null;
	}

	return (
		<Box mt={3}>
			<Tabs value={location.pathname}>
				<Tab
					label="Аналітика"
					value="/admin/analytic"
					to="/admin/analytic"
					component={Link}
				/>
				<Tab
					label="Користувачі"
					value="/admin/user"
					to="/admin/user"
					component={Link}
				/>
				<Tab
					label="Продукти"
					value="/admin/product"
					to="/admin/product"
					component={Link}
				/>
				<Tab
					label="Замовлення"
					value="/admin/order"
					to="/admin/order"
					component={Link}
				/>
				<Tab
					label="Поставки"
					value="/admin/delivery"
					to="/admin/delivery"
					component={Link}
				/>
				<Tab
					label="Постачальники"
					value="/admin/vendor"
					to="/admin/vendor"
					component={Link}
				/>

			</Tabs>
			<Box>
				<Outlet />
			</Box>
		</Box>
	);
};

export default Admin;