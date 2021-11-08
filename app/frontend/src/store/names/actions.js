import { ADD_NAME, UPDATE_NAME, DELETE_NAME } from '../action-types'

export const addName = name => {
	return {
		type: ADD_NAME,
		name,
	}
}

export const updateName = (name, nameId) => {
	return {
		type: UPDATE_NAME,
		name,
		nameId,
	}
}

export const deleteName = nameId => {
	return {
		type: DELETE_NAME,
		name: {},
		nameId,
	}
}
