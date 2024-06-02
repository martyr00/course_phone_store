import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
	Button,
	IconButton, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { IVendor } from '../../utils/types';
import { getVendorList } from '../../service/vendor';

const Vendor = () => {
	const [data, setData] = useState<IVendor[]>([]);

	const location = useLocation();
	const navigate = useNavigate();

	useEffect(() => {
		getVendorList()
			.then(setData)
			.catch(() => null);
	}, [location.pathname]);

	return (
		<TableContainer component={Paper}>
			<Button onClick={() => navigate('/admin/vendor/new')}>
				Додати постачальника
			</Button>
			<Table sx={{ minWidth: 650 }} aria-label="simple table">
				<TableHead>
					<TableRow>
						<TableCell>Id</TableCell>
						<TableCell>First Name</TableCell>
						<TableCell>Second Name</TableCell>
						<TableCell>Surname</TableCell>
						<TableCell>Number Telephone</TableCell>
						<TableCell>Created Time</TableCell>
						<TableCell>Count Deliveries</TableCell>
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
							<TableCell>{item.first_name}</TableCell>
							<TableCell>{item.second_name}</TableCell>
							<TableCell>{item.surname}</TableCell>
							<TableCell>{item.number_telephone}</TableCell>
							<TableCell>{item.created_time}</TableCell>
							<TableCell>{item.count_deliveries}</TableCell>

							<TableCell>
								<IconButton
									aria-label="edit"
									onClick={() => navigate(`/admin/vendor/${item.id}`)}
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

export default Vendor;