export const refReducer = (state = [], action) => {
	if (action.ref === undefined && action.name === undefined) return state
	let ret = null

	switch (action.type) {
		case 'ADD':
			ret = [...state, action.ref]
			break
		case 'UPDATE':
			ret = state.map(v => (v.id === action.ref.id ? action.ref : v))
			break
		case 'UPDATE_NAME': {
			ret = state.map(v => {
				if (v.id !== action.refId) return v

				return {
					...v,
					names: v.names.map(name =>
						name.id === action.nameId ? action.name : name
					),
				}
			})
			break
		}

		case 'ADD_NAME': {
			ret = state.map(v => {
				if (v.id !== action.refId) return v

				return {
					...v,
					names: v.names.concat(action.name),
				}
			})

			break
		}
		case 'DELETE': {
			ret = state.filter(v => v.id !== action.ref.id)
			break
		}
		default:
			ret = state
			break
	}

	return ret
}
