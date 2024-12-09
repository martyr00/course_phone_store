import React, { useEffect, useState } from 'react';
import {
	Box,
	FormControl,
	Grid,
	InputLabel,
	MenuItem,
	Paper,
	Select,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
} from '@mui/material';
import {
	getAnalyticBestSellingTelephone,
	getAnalyticMoreThanInWishList,
	getAnalyticVendorsByTelephonesBrand,
	getAnalyticUsersPlacedOrderOnDate,
	getAnalyticUsersByQuantityAndTotalCostOrder,
} from '../../service/analytic';
import { IBrand } from '../../utils/types';
import { getBrandList } from '../../service/brand';

const AnalyticsNew = () => {
	const [bestSellingTelephone, setBestSellingTelephone] = useState<{
		title: string;
		total_sells: number;
	}[]>([]);
	const [moreThanInWishList, setMoreThanInWishList] = useState<{
		title: string;
		quantity_added: number;
	}[]>([]);
	const [usersByQuantityAndTotalCostOrder, setUsersByQuantityAndTotalCostOrder] = useState<{
		id: number;
		first_name: string;
		second_name: string;
		last_name: string;
		quantity_orders: number;
		total_cost: number;
	}[]>([]);
	const [vendorsByTelephonesBrand, setVendorsByTelephonesBrand] = useState<{
		id: number;
		first_name: string;
		second_name: string;
		surname: string;
		number_telephone: string;
	}[]>([]);
	const [usersPlacedOrderOnDate, setUsersPlacedOrderOnDate] = useState<{
		username: string;
		first_name: string;
		second_name: string;
	}[]>([]);

	const [brandList, setBrandList] = useState<IBrand[]>([]);

	const [brand, setBrand] = useState('');
	const [date, setDate] = useState('');

	useEffect(() => {
		getBrandList()
			.then(setBrandList)
			.catch(() => null);

		const fetchDataCommon = async () => {
			try {
				const [
					bestSellingTelephoneData,
					moreThanInWishListData,
					usersByQuantityAndTotalCostOrderData,
				] = await Promise.all([
					getAnalyticBestSellingTelephone(),
					getAnalyticMoreThanInWishList(),
					getAnalyticUsersByQuantityAndTotalCostOrder(),
				]);

				setBestSellingTelephone(bestSellingTelephoneData);
				setMoreThanInWishList(moreThanInWishListData);
				setUsersByQuantityAndTotalCostOrder(usersByQuantityAndTotalCostOrderData);
			} catch (error) {
				// empty error
			}
		};

		fetchDataCommon();
	}, []);

	useEffect(() => {
		if (brand) {
			const fetchBrandData = async (brand: string) => {
				try {
					const vendorsByTelephonesBrandData = await getAnalyticVendorsByTelephonesBrand(brand);

					setVendorsByTelephonesBrand(vendorsByTelephonesBrandData);
				} catch (error) {
					// empty error
				}
			};

			fetchBrandData(brand);
		} else {
			setVendorsByTelephonesBrand([]);
		}
	}, [brand]);

	useEffect(() => {
		if (date) {
			const fetchDateData = async (date: string) => {
				try {
					const usersPlacedOrderOnDateData = await getAnalyticUsersPlacedOrderOnDate(date);

					setUsersPlacedOrderOnDate(usersPlacedOrderOnDateData);
				} catch (error) {
					// empty error
				}
			};

			fetchDateData(date);
		} else {
			setUsersPlacedOrderOnDate([]);
		}
	}, [date]);

	return (
		<>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Best Selling Telephone
				</Typography>
				<TableContainer component={Paper}>
					<Table sx={{ minWidth: 650, whiteSpace: 'nowrap' }} aria-label="simple table">
						<TableHead>
							<TableRow>
								<TableCell>Title</TableCell>
								<TableCell>Total Sells</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{bestSellingTelephone.map((item) => (
								<TableRow
									key={item.title}
									sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
								>
									<TableCell>{item.title}</TableCell>
									<TableCell>{item.total_sells}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					More Than In WishList
				</Typography>
				<TableContainer component={Paper}>
					<Table sx={{ minWidth: 650, whiteSpace: 'nowrap' }} aria-label="simple table">
						<TableHead>
							<TableRow>
								<TableCell>Title</TableCell>
								<TableCell>Quantity Added</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{moreThanInWishList.map((item) => (
								<TableRow
									key={item.title}
									sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
								>
									<TableCell>{item.title}</TableCell>
									<TableCell>{item.quantity_added}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Vendors By Telephones Brand
				</Typography>
				<Grid item xs={12} sm={6} mb={2}>
					<FormControl fullWidth>
						<InputLabel id="select-label-brand">Brand</InputLabel>
						<Select
							labelId="select-label-brand"
							value={brand}
							label="Brand"
							fullWidth
							onChange={(e) => {
								setBrand(e.target.value);
							}}
						>
							{brandList.map((option) => (
								<MenuItem key={option.title} value={option.title}>
									{option.title}
								</MenuItem>
							))}
						</Select>
					</FormControl>
				</Grid>
				<TableContainer component={Paper}>
					<Table sx={{ minWidth: 650, whiteSpace: 'nowrap' }} aria-label="simple table">
						<TableHead>
							<TableRow>
								<TableCell>Id</TableCell>
								<TableCell>First Name</TableCell>
								<TableCell>Second Name</TableCell>
								<TableCell>Surname</TableCell>
								<TableCell>Number Telephone</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{vendorsByTelephonesBrand.map((item) => (
								<TableRow
									key={item.id}
									sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
								>
									<TableCell>{item.id}</TableCell>
									<TableCell>{item.first_name}</TableCell>
									<TableCell>{item.second_name}</TableCell>
									<TableCell>{item.surname}</TableCell>
									<TableCell>{item.number_telephone}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Users Placed Order On Date
				</Typography>
				<div className="date-input-container">
					<input
						type="date"
						id="date-picker"
						value={date}
						onChange={(e) => setDate(e.target.value)}
						className="date-input-field"
					/>
				</div>
				<TableContainer component={Paper}>
					<Table sx={{ minWidth: 650, whiteSpace: 'nowrap' }} aria-label="simple table">
						<TableHead>
							<TableRow>
								<TableCell>username</TableCell>
								<TableCell>first_name</TableCell>
								<TableCell>second_name</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{usersPlacedOrderOnDate.map((item) => (
								<TableRow
									key={item.username}
									sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
								>
									<TableCell>{item.username}</TableCell>
									<TableCell>{item.first_name}</TableCell>
									<TableCell>{item.second_name}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Users By Quantity And Total Cost Order
				</Typography>
				<TableContainer component={Paper}>
					<Table sx={{ minWidth: 650, whiteSpace: 'nowrap' }} aria-label="simple table">
						<TableHead>
							<TableRow>
								<TableCell>Id</TableCell>
								<TableCell>First Name</TableCell>
								<TableCell>Second Name</TableCell>
								<TableCell>Last Name</TableCell>
								<TableCell>Quantity Orders</TableCell>
								<TableCell>Total Cost</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{usersByQuantityAndTotalCostOrder.map((item) => (
								<TableRow
									key={item.id}
									sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
								>
									<TableCell>{item.id}</TableCell>
									<TableCell>{item.first_name}</TableCell>
									<TableCell>{item.second_name}</TableCell>
									<TableCell>{item.last_name}</TableCell>
									<TableCell>{item.quantity_orders}</TableCell>
									<TableCell>{item.total_cost}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</Box>
		</>
	);
};

export default AnalyticsNew;