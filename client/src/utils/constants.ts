import { IShortProduct } from './types';

export const formatterCurrency = new Intl.NumberFormat('uk-UA', {
	style: 'currency',
	currency: 'UAH',
	minimumFractionDigits: 0,
	maximumFractionDigits: 0,
});

export const prepareShortProduct = (product: IShortProduct): IShortProduct => ({
	...product,
	images: product.images
		.filter((image) => image)
		.map((image) => (`${process.env.REACT_APP_MEDIA_BASE_URL}/${image}`)),
});
