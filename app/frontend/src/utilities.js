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
	'db_relation'
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

const dbIdRegex = /^db_/
export const isDbId = id => dbIdRegex.test(JSON.parse(id).type)

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

const DOI_REGEX_PATTERNS_FOR_URL_SEARCH = [
	/10.\d{4,9}\/[-._;()/:A-Z0-9]+$/i,
	/10.1002\/[^\s]+$/i,
	/10.\d{4}\/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d$/i,
	/10.1021\/\w\w\d+$/i,
	/10.1207\/[\w\d]+\&\d+_\d+$/i,
]

const extractDoiFromUrl = value => {
	let doiFound
	DOI_REGEX_PATTERNS_FOR_URL_SEARCH.some(regex => {
		doiFound = value.match(regex)
		if (doiFound) {
			return true
		}
		return false
	})
	if (doiFound) {
		return doiFound[0]
	}
	return doiFound
}

export const findDuplicateDois = value => {
	if (!value) return false
	const doi = extractDoiFromUrl(value)
	if (!doi) return false
	return loadServerData('references').some(v => {
		const databaseDoiFromUrl = v.link
			? extractDoiFromUrl(v.link)
			: undefined
		return v.doi
			? v.doi === doi
			: false || databaseDoiFromUrl
			? databaseDoiFromUrl === doi
			: false
	})
}

export const findDuplicateStructuredNames = (sname, structuredNames) =>
	loadServerData('structured_names')
		.concat(structuredNames)
		.filter(v => v.qualifier_id === sname.qualifier_id)
		.filter(v => v.location_id === sname.location_id)
		.filter(v => v.name_id === sname.name_id)
