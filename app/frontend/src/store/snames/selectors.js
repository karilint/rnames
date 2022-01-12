import { createSelector } from 'reselect'
import { parseId } from '../../utilities'

export const selectDbNames = state => {
	return Object.entries(state.map).filter(
		([key]) => parseId(key).type === 'db_name'
	)
}

export const selectNames = state => {
	return state.names.filter(name => name.variant === 'name')
}

export const selectAllNames = createSelector(
	[selectDbNames, selectNames],
	(dbNames, names) => {
		return dbNames
			.map(v => [v[1].id, v[1].name])
			.concat(names.map(v => [v.id, v.name]))
	}
)

export const selectDbLocations = state => {
	return Object.entries(state.map).filter(
		([key]) => parseId(key).type === 'db_location'
	)
}

export const selectLocations = state => {
	return state.names.filter(name => name.variant === 'location')
}

export const selectAllLocations = createSelector(
	[selectDbLocations, selectLocations],
	(dbLocations, locations) => {
		return dbLocations
			.map(v => [v[1].id, v[1].name])
			.concat(locations.map(v => [v.id, v.name]))
	}
)

export const selectRefence = state => {
	return state.ref[0]
}

export const selectMap = state => state.map
export const selectRelations = state => state.rel

export const selectSnames = state => state.sname

export const selectNamesAddedByUser = createSelector(
	[selectSnames, (state, snameId) => snameId],
	(snames, snameId) => {
		return snames
			.filter(v => {
				if (v.id === snameId) return false
				if (parseId(v.name_id).type === 'db_name') return false
				return true
			})
			.map(v => v.name_id)
	}
)

export const selectLocationsAddedByUser = createSelector(
	[selectSnames, (state, snameId) => snameId],
	(snames, snameId) => {
		return snames
			.filter(v => {
				if (v.id === snameId) return false
				if (parseId(v.location_id).type === 'db_location') return false
				return true
			})
			.map(v => v.location_id)
	}
)
