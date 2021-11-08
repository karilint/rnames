import { ADD, DELETE, UPDATE } from '../action-types'

export const addSname = sname => {
	return {
		type: ADD,
		sname,
	}
}

export const updateSname = sname => {
	return {
		type: UPDATE,
		sname,
	}
}

export const deleteSname = sname => {
	return {
		type: DELETE,
		sname,
	}
}
