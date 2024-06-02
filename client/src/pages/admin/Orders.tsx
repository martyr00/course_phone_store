import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
	IconButton, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { IOrder } from '../../utils/types';
import { getOrderList } from '../../service/order';

const Orders = () => {
	const [data, setData] = useState<IOrder[]>([]);

	const location = useLocation();
	const navigate = useNavigate();

	useEffect(() => {
		getOrderList()
			.then(setData)
			.catch(() => null);
	}, [location.pathname]);

	return (
		<TableContainer component={Paper}>
			<Table sx={{ minWidth: 650 }} aria-label="simple table">
				<TableHead>
					<TableRow>
						<TableCell>Id</TableCell>
						<TableCell>Status</TableCell>
						<TableCell>User Id</TableCell>
						<TableCell>Surname</TableCell>
						<TableCell>First Name</TableCell>
						<TableCell>Second Name</TableCell>
						<TableCell>Street</TableCell>
						<TableCell>Post Code</TableCell>
						<TableCell>Full Price</TableCell>
						<TableCell>Action</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{data.map((item) => (
						<TableRow
							key={item.id}
							sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
						>
							<TableCell>{item.id}</TableCell>
							<TableCell>{item.status}</TableCell>
							<TableCell>{item.user_id}</TableCell>
							<TableCell>{item.surname}</TableCell>
							<TableCell>{item.first_name}</TableCell>
							<TableCell>{item.second_name}</TableCell>
							<TableCell>{item.street}</TableCell>
							<TableCell>{item.post_code}</TableCell>
							<TableCell>{item.full_price}</TableCell>
							<TableCell>
								<IconButton
									aria-label="edit"
									onClick={() => navigate(`/admin/order/${item.id}`)}
								>
									<EditIcon />
								</IconButton>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</TableContainer>
	);
};

export default Orders;