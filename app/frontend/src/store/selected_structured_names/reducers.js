import {
	SELECT_STRUCTURED_NAME,
	DESELECT_STRUCTURED_NAME,
} from '../action-types.js'

export const selectedStructuredNamesReducer = (
	state = [],
	{ type, structured_name_id }
) => {
	if (structured_name_id === undefined) return state

	switch (type) {
		case SELECT_STRUCTURED_NAME: {
			if (state.includes(structured_name_id))
				return state
			else
				return state.concat(structured_name_id)
		}
		case DESELECT_STRUCTURED_NAME:
			return state.filter(v => v !== structured_name_id)
		default:
			return state
	}
}
