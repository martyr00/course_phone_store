/* eslint-disable @typescript-eslint/no-explicit-any */

type Actions = {
	[key: string]: (state: any, payload?: any) => any;
};

interface ISettings {
	moduleName: string;
}

export const ActionCreatorsFactory = <T>(
	settings: ISettings,
	actions: Actions,
): T => {
	const { moduleName } = settings;

	const result: any = {};

	Object.keys(actions).forEach((actionName) => {
		const type = `${moduleName}/${actionName}`;

		result[actionName] = (payload?: any) => ({ type, payload });
		result[actionName].type = type;
		result[type] = (state: any, payload: any) => actions[actionName](state, payload);
	});

	return result;
};

export const ReducerFactory = <T>(initialState: T, actions: any) => (
	state: T = initialState,
	action: { type: string; payload?: any } | null = null,
): T => {
	if (action && typeof actions[action.type] === 'function') {
		return actions[action.type](state, action.payload) || state;
	}

	return state;
};