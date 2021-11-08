import { ADD, DELETE, UPDATE } from '../action-types'

export const addRef = ref => {
	return {
		type: ADD,
		ref,
	}
}

export const updateRef = ref => {
	return {
		type: UPDATE,
		ref,
	}
}

export const deleteRef = ref => {
	return {
		type: DELETE,
		ref,
	}
}
