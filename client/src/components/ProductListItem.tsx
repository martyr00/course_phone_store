import React from 'react';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import { Link as RouterLink } from 'react-router-dom';
import Link from '@mui/material/Link';
import Box from '@mui/material/Box';
import { Grid } from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { IShortProduct } from '../utils/types';
import { formatterCurrency } from '../utils/constants';
import { actionsFavorite, selectFavoriteIds } from '../ducks/favorite';
import { actionsCompare, selectCompareIds } from '../ducks/compare';
import { actionsCart, selectCartItems } from '../ducks/cart';
import noImage from '../assets/noImage.jpg';
import { removeFromWishList, setToWishList } from '../service/wishlist';

const ProductListItem = ({
	id,
	title,
	brand,
	price,
	images,
}: IShortProduct) => {
	const dispatch = useDispatch();
	const cartItems = useSelector(selectCartItems);
	const favoriteIds = useSelector(selectFavoriteIds);
	const compareIds = useSelector(selectCompareIds);

	const handleClickFavorite = async () => {
		if (favoriteIds.includes(id)) {
			await removeFromWishList(id);
		} else {
			await setToWishList(id);
		}
		dispatch(actionsFavorite.toggleProduct(id));
	};

	const handleClickCompare = () => {
		dispatch(actionsCompare.toggleProduct(id));
	};

	const handleClickCart = () => {
		if (cartItems.find((i) => i.id === id)) {
			dispatch(actionsCart.decrementCartQuantity(id));
		} else {
			dispatch(actionsCart.increaseCartQuantity(id));
		}
	};

	return (
		<Grid
			item
			xl={3}
			lg={4}
			md={6}
			sm={6}
			xs={12}
		>
			<Card sx={{ margin: 1 }}>
				<Link component={RouterLink} to={`/product/${id}`} underline="none">
					<CardMedia
						component="img"
						height="300"
						sx={{ objectFit: 'contain' }}
						image={images[0] || noImage}
						alt={title}
					/>
				</Link>
				<CardContent>
					<Link component={RouterLink} to={`/product/${id}`} underline="none" color="inherit">
						<Typography gutterBottom variant="h5" component="div">
							{title}
						</Typography>
					</Link>
					<Box mt={1}>
						<Typography variant="h6">
							{`Бренд: ${brand}`}
						</Typography>
						<Typography variant="h6">
							{`Ціна: ${formatterCurrency.format(price)}`}
						</Typography>
					</Box>
				</CardContent>
				<CardActions>
					<Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
						<Box>
							<IconButton
								aria-label="add to favorite"
								color={favoriteIds.includes(id) ? 'success' : 'info'}
								onClick={handleClickFavorite}
							>
								<FavoriteIcon />
							</IconButton>
							<IconButton
								aria-label="add to compare"
								color={compareIds.includes(id) ? 'success' : 'info'}
								onClick={handleClickCompare}
							>
								<CompareArrowsIcon />
							</IconButton>
						</Box>
						<Button size="small">
							<Button
								color={cartItems.find((i) => i.id === id) ? 'success' : 'info'}
								variant="contained"
								onClick={handleClickCart}
							>
								{cartItems.find((i) => i.id === id) ? 'Видалити з кошику' : 'Додати в кошик'}
							</Button>
						</Button>
					</Box>
				</CardActions>
			</Card>
		</Grid>
	);
};

export default ProductListItem;
