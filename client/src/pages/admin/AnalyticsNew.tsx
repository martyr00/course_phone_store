import React, {useEffect, useState} from 'react';
import {
    getAnalyticBestSellingTelephone,
    getAnalyticMoreThanInWishList,
    getAnalyticVendorsByTelephonesBrand,
    getAnalyticUsersPlacedOrderOnDate,
    getAnalyticUsersByQuantityAndTotalCostOrder,
} from '../../service/analytic';

const AnalyticsNew = () => {
    const [views, setViews] = useState<[]>([]);

    const fetchData = async () => {
        try {
            const [
                BestSellingTelephoneData,
            ] = await Promise.all([
                getAnalyticBestSellingTelephone(),
                getAnalyticMoreThanInWishList(),
                getAnalyticUsersByQuantityAndTotalCostOrder(),
            ]);

            setViews(BestSellingTelephone);
        } catch (error) {
            // empty error
        }
    };

	useEffect(() => {
		fetchData();
	}, []);

    return (
        <div>

        </div>
    );
};

export default AnalyticsNew;