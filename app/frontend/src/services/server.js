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

	SERVER_DATA.amendInfo = load('AMEND_INFO')
	if (SERVER_DATA.amendInfo.amend === true) {
		const referenceId = makeId('db_reference', SERVER_DATA.amendInfo.referenceId)
		SERVER_DATA.amendInfo.relations = SERVER_DATA.amendInfo.relations.map(v => ({
			id: makeId('db_relation', v.id),
			belongs_to: v.belongs_to,
			name1: makeId('db_structured_name', v.name_one_id),
			name2: makeId('db_structured_name', v.name_two_id),
			reference_id: referenceId
		}))
		SERVER_DATA.amendInfo.referenceId = referenceId
	}
}

export const loadServerData = (k) => k === undefined ? SERVER_DATA : SERVER_DATA[k]