import { ADD, UPDATE, DELETE } from '../action-types'

export const addRel = rel => {
	return {
		type: ADD,
		rel,
	}
}

export const updateRel = rel => {
	return {
		type: UPDATE,
		rel,
	}
}

export const deleteRel = rel => {
	return {
		type: DELETE,
		rel,
	}
}
