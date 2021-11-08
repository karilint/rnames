export const mapReducer = (state = {}, action) => {
	let k, v

	switch (action.type) {
		case 'ADD_NAME': {
			v = action.name
			k = v.id
			break
		}

		case 'UPDATE_NAME': {
			v = action.name
			k = v.id
			break
		}

		case 'DELETE_NAME': {
			let updatedState = { ...state }
			delete updatedState[action.nameId]
			return updatedState
		}

		case 'ADD': {
			v = action.ref || action.sname || action.rel
			k = v.id
			break
		}

		case 'UPDATE': {
			v = action.ref || action.sname || action.rel
			k = v.id
			break
		}

		case 'MAP_VALUE': {
			v = action.value
			k = action.key
			break
		}

		case 'INITIALIZE_MAP_VALUES': {
			return action.map
		}
		case 'DELETE': {
			v = action.sname || action.rel || action.ref
			let updatedState = { ...state }
			delete updatedState[v.id]
			return updatedState
		}

		default:
			return state
	}

	const ret = { ...state }
	ret[k] = v
	return ret
}
