export const nameReducer = (names = [], action) => {
	if (action.name === undefined) return names

	switch (action.type) {
		case 'ADD_NAME': {
			return names.concat(action.name)
		}
		case 'UPDATE_NAME': {
			return names.map(name =>
				name.id === action.nameId ? action.name : name
			)
		}
		case 'DELETE_NAME': {
			return names.filter(name => name.id !== action.nameId)
		}
		default:
			return names
	}
}
