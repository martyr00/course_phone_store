import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { actionsFavorite } from '../ducks/favorite';
import { getWishList } from '../service/wishlist';

const FavoriteProvider = () => {
	const dispatch = useDispatch();

	const fetchServerData = async () => {
		const res = await getWishList();

		const ids = res.map(({ telephone_id }) => telephone_id);

		dispatch(actionsFavorite.setItems(ids));
	};

	useEffect(() => {
		fetchServerData();
	}, []);

	return null;
};

export default FavoriteProvider;