import React, { useEffect, useState } from 'react';
import {
	Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { useNavigate } from 'react-router-dom';
import { IUser } from '../../utils/types';
import { getAdminUserList } from '../../service/user';

const Users = () => {
	const [data, setData] = useState<IUser[]>([]);

	const navigate = useNavigate();

	useEffect(() => {
		getAdminUserList()
			.then(setData)
			.catch(() => null);
	}, []);

	return (
		<TableContainer component={Paper}>
			<Table sx={{ minWidth: 650, whiteSpace: 'nowrap' }} aria-label="simple table">
				<TableHead>
					<TableRow>
						<TableCell>ID</TableCell>
						<TableCell>Last Login</TableCell>
						<TableCell>Username</TableCell>
						<TableCell>First Name</TableCell>
						<TableCell>Second Name</TableCell>
						<TableCell>Surname</TableCell>
						<TableCell>Email</TableCell>
						<TableCell>Date Joined</TableCell>
						<TableCell>Image</TableCell>
						<TableCell>Number Telephone</TableCell>
						<TableCell>Actions</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{data.map((user) => (
						<TableRow
							key={user.id}
							sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
						>
							<TableCell>{user.id}</TableCell>
							<TableCell>{user.last_login}</TableCell>
							<TableCell>{user.username}</TableCell>
							<TableCell>{user.first_name}</TableCell>
							<TableCell>{user.second_name}</TableCell>
							<TableCell>{user.surname}</TableCell>
							<TableCell>{user.email}</TableCell>
							<TableCell>{user.date_joined}</TableCell>
							<TableCell>{user.image}</TableCell>
							<TableCell>{user.number_telephone}</TableCell>
							<TableCell>
								<IconButton
									aria-label="edit"
									onClick={() => navigate(`/admin/user/${user.id}`)}
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

export default Users;