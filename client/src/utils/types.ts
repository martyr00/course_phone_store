export enum EnumLocalStorageKey {
	accessToken = 'accessToken',
	refreshToken = 'refreshToken',
	compareItems = 'compareItems',
	cartItems = 'cartItems',
	favoriteItems = 'favoriteItems',
}

export interface IUser {
	id: number,
	last_login: string | null,
	is_superuser: boolean,
	username: string,
	first_name: string,
	second_name: string,
	surname: string,
	email: string,
	is_staff: boolean,
	is_active: boolean,
	date_joined: string,
	image: string,
	number_telephone: null
}

export interface IOrder {
	id: number,
	status: string,
	user_id: number,
	surname: string,
	first_name: string,
	second_name: string,
	street: string,
	post_code: string,
	full_price: number
}

export interface IOrderItem extends IOrder {
	order_product_details: {
		id: number,
		price: number,
		amount: number,
		order_id: number,
		telephone_id: number,
		created_time: string,
	}[]
}

export interface IShortProduct {
	id: number,
	title: string,
	price: number,
	brand: string,
	brand_id: number,
	images: (string | null)[]
}

export interface IDetailProduct extends IShortProduct {
	description: string,
	diagonal_screen: number,
	built_in_memory: string,
	weight: number,
	number_stock: number,
	discount: number,
	release_date: string,
}

export interface IBrand {
	id: number,
	title: string,
}

export interface IProductEditCreateData {
	title: string
	description: string
	diagonal_screen: number
	built_in_memory: string
	price: number
	discount: number
	weight: number
	number_stock: number
	release_date: string
	brand_id: number
}

export interface IRegistrationData {
	password: string,
	username: string,
	first_name: string,
	surname: string,
	email: string,
	userprofile: {
		number_telephone: string,
		birth_date: string,
		second_name: string,
	}
}

export interface IAnalyticItem {
	date: string,
	value: string,
}

export interface ICreateOrder {
	'first_name': string;
	'second_name': string;
	'surname': string;
	'email': string;
	'number_telephone': string;
	'address':{
		'street_name': string
		'city_id': number,
		'post_code': string
	},
	'products':{
		'amount': number,
		'telephone_id': number
	}[]
}

export interface ICity {
	id: number,
	name: string,
}

export interface IDeliveryItem {
	delivery_id: number,
	delivery_price: number,
	vendor_id: number,
	full_name: string,
}

export interface IDeliveryCreateEdit {
	vendor_id: number,
	delivery_details: {
		price_one_phone: number,
		amount: number,
		telephone_id: number,
	}[]
}

export interface IVendor {
	id?: number
	first_name: string
	second_name: string
	surname: string
	number_telephone: string
	created_time?: string
	count_deliveries?: number
}
