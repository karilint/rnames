import { MAP_VALUE, INITIALIZE_MAP_VALUES } from '../action-types'

export const mapId = (key, value) => {
	return {
		type: MAP_VALUE,
		key,
		value,
	}
}

export const initMapvalues = map => {
	return {
		type: INITIALIZE_MAP_VALUES,
		map,
	}
}
