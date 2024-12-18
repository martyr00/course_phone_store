import React, { useEffect, useState } from 'react';
import {
	Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Button,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { useLocation, useNavigate } from 'react-router-dom';
import { IDetailProduct } from '../../utils/types';
import { deleteProductItem, getAdminProductList } from '../../service/product';

const Products = () => {
	const [data, setData] = useState<IDetailProduct[]>([]);

	const location = useLocation();
	const navigate = useNavigate();

	useEffect(() => {
		getAdminProductList()
			.then(setData)
			.catch(() => null);
	}, [location.pathname]);

	const handleDelete = async (id: number) => {
		await deleteProductItem(id);

		getAdminProductList()
			.then(setData)
			.catch(() => null);
	};

	return (
		<TableContainer component={Paper}>
			<Button onClick={() => navigate('/admin/product/new')}>
				Додати товар
			</Button>
			<Table sx={{ minWidth: 650 }} aria-label="simple table">
				<TableHead>
					<TableRow sx={{ whiteSpace: 'nowrap', fontWeight: 600 }}>
						<TableCell>Id</TableCell>
						<TableCell>Title</TableCell>
						<TableCell>Price</TableCell>
						<TableCell>Brand</TableCell>
						<TableCell>Description</TableCell>
						<TableCell>Diagonal Screen</TableCell>
						<TableCell>Built In Memory</TableCell>
						<TableCell>Weight</TableCell>
						<TableCell>Number Stock</TableCell>
						<TableCell>Discount</TableCell>
						<TableCell>Release Date</TableCell>
						<TableCell>Actions</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{data.map((item) => (
						<TableRow
							key={item.id}
							sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
						>
							<TableCell>{item.id}</TableCell>
							<TableCell>{item.title}</TableCell>
							<TableCell>{item.price}</TableCell>
							<TableCell>{item.brand}</TableCell>
							<TableCell>{item.description}</TableCell>
							<TableCell>{item.diagonal_screen}</TableCell>
							<TableCell>{item.built_in_memory}</TableCell>
							<TableCell>{item.weight}</TableCell>
							<TableCell>{item.number_stock}</TableCell>
							<TableCell>{item.discount}</TableCell>
							<TableCell>{item.release_date}</TableCell>
							<TableCell>
								<div style={{ display: 'flex', gap: '10px' }}>
									<IconButton
										aria-label="edit"
										onClick={() => navigate(`/admin/product/${item.id}`)}
									>
										<EditIcon />
									</IconButton>
									<IconButton
										aria-label="delete"
										onClick={() => handleDelete(item.id)}
									>
										<DeleteIcon />
									</IconButton>
								</div>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</TableContainer>
	);
};

export default Products;