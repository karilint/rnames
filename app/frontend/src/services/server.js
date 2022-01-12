import { makeId } from '../utilities'

const SERVER_DATA = {}

export const initServer = () => {
	const load = (id) => JSON.parse(document.getElementById(id).textContent)
	SERVER_DATA.names = load('DATA_NAMES')
		.map(v => {
			return { ...v, id: makeId('db_name', v.id) }
		})

	SERVER_DATA.locations =  load('DATA_LOCATIONS')
		.map(v => {
			return { ...v, id: makeId('db_location', v.id) }
		})

	SERVER_DATA.qualifier_names = load('DATA_QUALIFIER_NAMES')
		.map(v => {
			return { ...v, id: makeId('db_qualifier_name', v.id) }
		})

	SERVER_DATA.qualifiers = load('DATA_QUALIFIERS')
		.map(v => {
			return {
				...v,
				id: makeId('db_qualifier', v.id),
				qualifier_name_id: makeId('db_qualifier_name', v.qualifier_name_id)
			}
		})

	SERVER_DATA.structured_names = load('DATA_STRUCTURED_NAMES')
		.map(v => {
			return {
				...v,
				id: makeId('db_structured_name', v.id),
				name_id: makeId('db_name', v.name_id),
				qualifier_id: makeId('db_qualifier', v.qualifier_id),
				reference_id: makeId('db_reference', v.reference_id),
				location_id: makeId('db_location', v.location_id)
			}
		})

	SERVER_DATA.references = load('DATA_REFERENCES')
		.map(v => {
			return { ...v, id: makeId('db_reference', v.id) }
		})
}

export const loadServerData = (k) => k === undefined ? SERVER_DATA : SERVER_DATA[k]