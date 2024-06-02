import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
	Button,
	IconButton, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { IDeliveryItem } from '../../utils/types';
import { getDeliveryList } from '../../service/delivery';

const Delivery = () => {
	const [data, setData] = useState<IDeliveryItem[]>([]);

	const location = useLocation();
	const navigate = useNavigate();

	useEffect(() => {
		getDeliveryList()
			.then(setData)
			.catch(() => null);
	}, [location.pathname]);

	return (
		<TableContainer component={Paper}>
			<Button onClick={() => navigate('/admin/delivery/new')}>
				Додати поставку
			</Button>
			<Table sx={{ minWidth: 650 }} aria-label="simple table">
				<TableHead>
					<TableRow>
						<TableCell>Delivery Id</TableCell>
						<TableCell>Delivery Price</TableCell>
						<TableCell>Vendor Id</TableCell>
						<TableCell>Full Name</TableCell>
						<TableCell>Action</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{data.map((item) => (
						<TableRow
							key={`${item.delivery_id}_${item.delivery_price}_${item.vendor_id}_${item.full_name}`}
							sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
						>
							<TableCell>{item.delivery_id}</TableCell>
							<TableCell>{item.delivery_price}</TableCell>
							<TableCell>{item.vendor_id}</TableCell>
							<TableCell>{item.full_name}</TableCell>

							<TableCell>
								<IconButton
									aria-label="edit"
									onClick={() => navigate(`/admin/delivery/${item.delivery_id}`)}
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

export default Delivery;