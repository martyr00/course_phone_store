import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { selectCompareIds } from '../ducks/compare';
import { EnumLocalStorageKey } from '../utils/types';

const CompareProvider = () => {
	const compareIds = useSelector(selectCompareIds);

	useEffect(() => {
		localStorage.setItem(
			EnumLocalStorageKey.compareItems,
			JSON.stringify(compareIds),
		);
	}, [JSON.stringify(compareIds)]);

	return null;
};

export default CompareProvider;