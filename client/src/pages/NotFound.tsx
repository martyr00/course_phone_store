import React from 'react';
import {
	Box, Button, Container, Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const NotFound: React.FC = () => (
	<Container component="main" maxWidth="md" sx={{ textAlign: 'center', mt: 5 }}>
		<Box sx={{ mt: 5 }}>
			<Typography variant="h2" component="h1" gutterBottom>
				404
			</Typography>
			<Typography variant="h5" component="h2" gutterBottom>
				Сторінка не знайдена
			</Typography>
			<Typography variant="body1" gutterBottom>
				Вибачте, але сторінка, яку ви шукаєте, не існує.
			</Typography>
			<Button
				variant="contained"
				color="primary"
				component={RouterLink}
				to="/"
				sx={{ mt: 3 }}
			>
				На головну
			</Button>
		</Box>
	</Container>
);

export default NotFound;
