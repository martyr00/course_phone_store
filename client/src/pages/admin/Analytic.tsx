import React, { useEffect, useState } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
	Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement,
} from 'chart.js';
import {
	Container, Typography, CircularProgress, Box,
} from '@mui/material';
import {
	getAnalyticView,
	getAnalyticAvgOrderCost,
	getAnalyticOrderAmount,
	getAnalyticOrderTotalSum,
	getAnalyticOrderAmountProduct,
	getAnalyticOrderProductPercentSales,
} from '../../service/analytic';

interface IAnalyticItem {
	date: string;
	value: string;
}

interface IChartData {
	telephone_title: string;
	total_sold: number;
}

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

Chart.register(ArcElement, Tooltip, Legend);

const AnalyticsPage: React.FC = () => {
	const [views, setViews] = useState<IAnalyticItem[]>([]);
	const [avgOrderCost, setAvgOrderCost] = useState<IAnalyticItem[]>([]);
	const [orderAmount, setOrderAmount] = useState<IAnalyticItem[]>([]);
	const [orderTotalSum, setOrderTotalSum] = useState<IAnalyticItem[]>([]);
	const [orderAmountProduct, setOrderAmountProduct] = useState<IAnalyticItem[]>([]);
	const [orderProductPercentSales, setOrderProductPercentSales] = useState<IChartData[]>([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const [
					viewsData,
					avgOrderCostData,
					orderAmountData,
					orderTotalSumData,
					orderAmountProductData,
					orderProductPercentSalesData,
				] = await Promise.all([
					getAnalyticView(),
					getAnalyticAvgOrderCost(),
					getAnalyticOrderAmount(),
					getAnalyticOrderTotalSum(),
					getAnalyticOrderAmountProduct(),
					getAnalyticOrderProductPercentSales(),
				]);

				setViews(viewsData);
				setAvgOrderCost(avgOrderCostData);
				setOrderAmount(orderAmountData);
				setOrderTotalSum(orderTotalSumData);
				setOrderAmountProduct(orderAmountProductData);
				setOrderProductPercentSales(orderProductPercentSalesData);
			} catch (error) {
				// empty error
			} finally {
				setLoading(false);
			}
		};

		fetchData();
	}, []);

	if (loading) {
		return (
			<Container style={{ textAlign: 'center', marginTop: '50px' }}>
				<CircularProgress />
				<Typography variant="h6">Завантаження даних...</Typography>
			</Container>
		);
	}

	const generateChartData = (data: IAnalyticItem[]) => ({
		labels: data.map((item) => item.date),
		datasets: [
			{
				label: '',
				data: data.map((item) => (item.value || 0)),
				borderColor: 'rgba(75,192,192,1)',
				backgroundColor: 'rgba(75,192,192,0.2)',
				fill: true,
			},
		],
	});

	const generateChartDataProductPercentSales = (data: IChartData[]) => ({
		labels: data.map((item) => item.telephone_title),
		datasets: [
			{
				data: data.map((item) => item.total_sold || 0),
				borderColor: data.map((item, index) => (
					`hsl(${Math.ceil((360 / data.length) * index)}, 50%, 50%)`
				)),
				backgroundColor: data.map((item, index) => (
					`hsl(${Math.ceil((360 / data.length) * index)}, 50%, 50%)`
				)),
				borderWidth: 1,
			},
		],
	});

	const options = { plugins: { legend: { display: false } } };

	return (
		<Box my={3}>
			<Typography variant="h4" gutterBottom>
				Аналітика
			</Typography>
			<Box my={3} sx={{ maxHeight: '80vh', margin: 'auto' }}>
				<Typography variant="h6" gutterBottom>
					Продажі телефонів
				</Typography>
				<Doughnut data={generateChartDataProductPercentSales(orderProductPercentSales)} />
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom>
					Перегляди
				</Typography>
				<Line options={options} data={generateChartData(views)} />
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Середня вартість замовлення
				</Typography>
				<Line options={options} data={generateChartData(avgOrderCost)} />
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Кількість замовлень
				</Typography>
				<Line options={options} data={generateChartData(orderAmount)} />
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Загальна сума замовлень
				</Typography>
				<Line options={options} data={generateChartData(orderTotalSum)} />
			</Box>
			<Box my={3}>
				<Typography variant="h6" gutterBottom style={{ marginTop: '40px' }}>
					Кількість продуктів у замовленнях
				</Typography>
				<Line options={options} data={generateChartData(orderAmountProduct)} />
			</Box>
		</Box>
	);
};

export default AnalyticsPage;
