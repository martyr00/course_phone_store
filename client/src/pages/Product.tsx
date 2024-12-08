import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
	Box, Button, Container, Grid, Paper, Typography, IconButton,
} from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import Slider from 'react-slick';
import { useDispatch, useSelector } from 'react-redux';
import { IDetailProduct } from '../utils/types';
import noImage from '../assets/noImage.jpg';
import { actionsCart, selectCartItems } from '../ducks/cart';
import { actionsFavorite, selectFavoriteIds } from '../ducks/favorite';
import { getProductItem } from '../service/product';
import { actionsCompare, selectCompareIds } from '../ducks/compare';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import { removeFromWishList, setToWishList } from '../service/wishlist';

const Product = () => {
	const { id } = useParams<{ id: string }>();
	const [product, setProduct] = React.useState<IDetailProduct | null>(null);

	const productId = Number(id);

	const discountedPrice = product
		? (product.price - (product.price * product.discount) / 100).toFixed(2)
		: null;

	const settings = {
		dots: true,
		infinite: true,
		speed: 500,
		slidesToShow: 1,
		slidesToScroll: 1,
	};

	const dispatch = useDispatch();
	const navigate = useNavigate();
	const cartItems = useSelector(selectCartItems);
	const favoriteIds = useSelector(selectFavoriteIds);
	const compareIds = useSelector(selectCompareIds);

	const handleClickFavorite = async () => {
		if (favoriteIds.includes(productId)) {
			await removeFromWishList(productId);
		} else {
			await setToWishList(productId);
		}
		dispatch(actionsFavorite.toggleProduct(productId));
	};

	const handleClickCompare = () => {
		dispatch(actionsCompare.toggleProduct(productId));
	};

	const handleClickCart = () => {
		if (cartItems.find((i) => i.id === productId)) {
			dispatch(actionsCart.decrementCartQuantity(productId));
		} else {
			dispatch(actionsCart.increaseCartQuantity(productId));
		}
	};

	const getDataFromServer = async () => {
		try {
			const res = await getProductItem(productId);

			setProduct({
				...res,
				images: res.images
					.filter((image) => image)
					.map((image) => (`${process.env.REACT_APP_MEDIA_BASE_URL}/${image}`)),
			});
		} catch (e) {
			navigate('/404');
		}
	};

	useEffect(() => {
		if (!productId) {
			navigate('/404');
		} else {
			getDataFromServer();
		}
	}, [productId]);

	if (!product) {
		return null;
	}

	return (
		<Container component="main" maxWidth="md" sx={{ mt: 8 }}>
			<Paper sx={{ padding: 3 }}>
				<Grid container spacing={4}>
					<Grid item xs={12} sm={6}>
						<Slider {...settings}>
							{product.images.map((image) => (
								<div key={image}>
									<img src={image || noImage} alt={product.title} style={{ width: '100%' }} />
								</div>
							))}
						</Slider>
					</Grid>
					<Grid item xs={12} sm={6}>
						<Typography variant="h4" component="h1" gutterBottom>
							{product.title}
						</Typography>
						<Typography variant="h5" color="text.secondary" gutterBottom>
							{product.brand}
						</Typography>
						<Typography variant="h6" color="text.primary" gutterBottom>
							{discountedPrice}
							{' '}
							грн
							{product.discount > 0 && (
								<Typography variant="body2" color="text.secondary" sx={{ textDecoration: 'line-through', ml: 1 }}>
									{product.price.toFixed(2)}
									{' '}
									грн
								</Typography>
							)}
						</Typography>
						<Typography variant="body1" paragraph>
							{product.description}
						</Typography>
						<Typography variant="body2" color="text.secondary" paragraph>
							{`Діагональ екрану: ${product.diagonal_screen}"`}
						</Typography>
						<Typography variant="body2" color="text.secondary" paragraph>
							{`Вбудована пам'ять: ${product.built_in_memory}`}
						</Typography>
						<Typography variant="body2" color="text.secondary" paragraph>
							{`Вага: ${product.weight}`}
						</Typography>
						<Typography variant="body2" color="text.secondary" paragraph>
							{`В наявності: ${product.number_stock}шт.`}
						</Typography>
						<Typography variant="body2" color="text.secondary" paragraph>
							{`Дата випуску: ${product.release_date}`}
						</Typography>
						<Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
							<Box>
								<IconButton
									aria-label="add to favorite"
									color={favoriteIds.includes(product.id) ? 'success' : 'info'}
									onClick={handleClickFavorite}
								>
									<FavoriteIcon />
								</IconButton>
								<IconButton
									aria-label="add to compare"
									color={compareIds.includes(product.id) ? 'success' : 'info'}
									onClick={handleClickCompare}
								>
									<CompareArrowsIcon />
								</IconButton>
							</Box>
							<Button size="small">
								<Button
									color={cartItems.find((i) => i.id === product.id) ? 'success' : 'info'}
									variant="contained"
									onClick={handleClickCart}
								>
									{cartItems.find((i) => i.id === product.id) ? 'Видалити з кошику' : 'Додати в кошик'}
								</Button>
							</Button>
						</Box>
					</Grid>
				</Grid>
			</Paper>
		</Container>
	);
};

export default Product;
