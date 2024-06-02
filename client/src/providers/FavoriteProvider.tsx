import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { selectFavoriteIds } from '../ducks/favorite';
import { EnumLocalStorageKey } from '../utils/types';

const FavoriteProvider = () => {
	const favoriteIds = useSelector(selectFavoriteIds);

	useEffect(() => {
		localStorage.setItem(
			EnumLocalStorageKey.favoriteItems,
			JSON.stringify(favoriteIds),
		);
	}, [JSON.stringify(favoriteIds)]);

	return null;
};

export default FavoriteProvider;