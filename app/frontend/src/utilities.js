import { loadServerData } from './services/server'

const idTypes = [
	'name',
	'location',
	'qualifier',
	'structured_name',
	'reference',
	'relation',
	'db_name',
	'db_location',
	'db_qualifier_name',
	'db_qualifier',
	'db_structured_name',
	'db_reference',
]

let ID = 0

export const parseId = id => JSON.parse(id)

export const makeId = (ty, value) => {
	if (!idTypes.includes(ty))
		throw new Error(`Id type must not be one of allowed types, was "${ty}"`)

	const id = value === undefined ? ID++ : Number(value)
	const idString = JSON.stringify({ type: ty, value: id })
	return idString
}

const findRef = (refs, ids) =>
	refs.find(ref => ref.names.find(v => ids.includes(v.id)))

const findId = (state, id) => state.map[id]

export const formatQualifier = (qualifier, state) => {
	if (qualifier === undefined) return ''

	const idObject = parseId(qualifier.id)
	if (idObject.type !== 'qualifier' && idObject.type !== 'db_qualifier')
		throw new Error(
			`Object with id ${qualifier.id} is not a structured name.`
		)

	// This distinction is necessary since the wizard assumes defining a new qualifier includes
	// defining a new name so the name is stored directly in the qualifier
	const qualifierName =
		idObject.type === 'db_qualifier'
			? findId(state, qualifier.qualifier_name_id)
			: qualifier

	return qualifierName ? qualifierName.name : ''
}

export const formatStructuredName = (structuredName, state) => {
	const idObject = parseId(structuredName.id)
	if (
		idObject.type !== 'structured_name' &&
		idObject.type !== 'db_structured_name'
	)
		throw new Error(
			`Object with id ${structuredName.id} is not a structured name.`
		)

	const name = findId(state, structuredName.name_id)
	const qualifierName = formatQualifier(
		findId(state, structuredName.qualifier_id),
		state
	)
	const location = findId(state, structuredName.location_id)
	return `${name ? name.name : ''} / ${qualifierName} / ${
		location ? location.name : ''
	}`
}

export const findDuplicateDois = doi =>
	loadServerData('references').filter(v => v.doi === doi)

export const findDuplicateLinks = doi =>
	loadServerData('references').filter(v => v.link === doi)

export const findDuplicateStructuredNames = (sname, structuredNames) =>
	loadServerData('structured_names')
		.concat(structuredNames)
		.filter(v => v.qualifier_id === sname.qualifier_id)
		.filter(v => v.location_id === sname.location_id)
		.filter(v => v.name_id === sname.name_id)
