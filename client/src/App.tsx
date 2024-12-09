import React from 'react';
import Container from '@mui/material/Container';
import CustomProviders from './providers/CustomProviders';
import Header from './components/Header';
import Routing from './Routing';
import './style.css';

const App = () => (
	<CustomProviders>
		<Header />
		<Container maxWidth="xl">
			<Routing />
		</Container>
	</CustomProviders>

);

export default App;