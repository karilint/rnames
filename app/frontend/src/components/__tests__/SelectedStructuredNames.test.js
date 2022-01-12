import React from 'react'
import { createStore, combineReducers, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import { SelectedStructuredNames } from '../SelectedStructuredNames'
import { Provider } from 'react-redux'
import { refReducer } from '../../store/references/reducers'
import { snameReducer } from '../../store/snames/reducers'
import { relReducer } from '../../store/relations/reducers'
import { selectedStructuredNamesReducer } from '../../store/selected_structured_names/reducers'
import { addRel } from '../../store/relations/actions'
import { selectStructuredName } from '../../store/selected_structured_names/actions'
import { makeId } from '../../utilities'
import { mapReducer } from '../../store/map/reducers'
import { nameReducer } from '../../store/names/reducers'
import * as server from '../../services/server'
import { initMapvalues } from '../../store/map/actions'

const mockStore = configureStore([])
jest.spyOn(server, 'loadServerData')

const reference = {
	firstAuthor: 'Úna C. Farrell',
	year: 2009,
	title: "Beyond Beecher's Trilobite Bed: Widespread pyritization of soft tissues in the Late Ordovician Taconic foreland basin",
	doi: '10.1130/g30177a.1',
	link: 'https://pubs.geoscienceworld.org/gsa/geology/article-abstract/37/10/907/103864/Beyond-Beecher-s-Trilobite-Bed-Widespread',
	exists: false,
	queried: true,
	edit: false,
	id: '{"type":"db_reference","value":30590}',
}

const dbStructuredName1 = {
	id: '{"type":"db_structured_name","value":1296}',
	name_id: '{"type":"db_name","value":1126}',
	location_id: '{"type":"db_location","value":70}',
	qualifier_id: '{"type":"db_qualifier","value":7}',
	reference_id: '{"type":"db_reference","value":0}',
	remarks: null,
	formattedName: 'Yeoman / Formation / Saskatchewan',
}

const dbSname1Formatted = 'Yeoman / Formation / Saskatchewan (1296)'

const dbStructuredName2 = {
	id: '{"type":"db_structured_name","value":5031}',
	location_id: '{"type":"db_location","value":1}',
	name_id: '{"type":"db_name","value":4644}',
	qualifier_id: '{"type":"db_qualifier","value":5}',
	reference_id: '{"type":"db_reference","value":0}',
	remarks: null,
	formattedName: 'Aalenian / Stage / Global',
}

const relation = {
	id: makeId('relation'),
	name1: dbStructuredName1.id,
	name2: makeId('structured_name'),
	reference_id: -1,
}

const initialMapState = {
	[dbStructuredName1.id]: {
		...dbStructuredName1,
	},
	[dbStructuredName1.name_id]: {
		id: [dbStructuredName1.name_id],
		name: 'Yeoman',
	},
	[dbStructuredName1.location_id]: {
		id: [dbStructuredName1.location_id],
		name: 'Saskatchewan',
	},
	[dbStructuredName1.qualifier_id]: {
		id: [dbStructuredName1.qualifier_id],
		level: 2,
		qualifier_name_id: '{"type":"db_qualifier_name","value":7}',
		stratigraphic_qualifier_id: 2,
	},
	'{"type":"db_qualifier_name","value":7}': {
		id: '{"type":"db_qualifier_name","value":7}',
		name: 'Formation',
	},
	[dbStructuredName2.id]: {
		...dbStructuredName2,
	},
	[dbStructuredName2.name_id]: {
		id: [dbStructuredName2.name_id],
		name: 'Aalenian',
	},
	[dbStructuredName2.location_id]: {
		id: [dbStructuredName2.location_id],
		name: 'Global',
	},
	[dbStructuredName2.qualifier_id]: {
		id: [dbStructuredName2.qualifier_id],
		level: 5,
		qualifier_name_id: '{"type":"db_qualifier_name","value":5}',
		stratigraphic_qualifier_id: 1,
	},
	'{"type":"db_qualifier_name","value":5}': {
		id: '{"type":"db_qualifier_name","value":5}',
		name: 'Stage',
	},
}

describe('When no existing structured names selected', () => {
	let store
	beforeEach(() => {
		jest.clearAllMocks()
		store = mockStore({
			map: mapReducer(initialMapState, { type: 'INIT' }),
			rel: relReducer([], { type: 'INIT', rel: {} }),
			selectedStructuredNames: selectedStructuredNamesReducer([], {
				type: 'INIT',
				structured_name_id: 9080,
			}),
		})
		store.dispatch = jest.fn()
		server.loadServerData.mockImplementation(k => [
			dbStructuredName1,
			dbStructuredName2,
		])
		render(
			<Provider store={store}>
				<SelectedStructuredNames />
			</Provider>
		)
	})

	test('has text "Select existing name"', () => {
		const label = screen.getByText(/Select existing name/i)
		expect(label).toBeInTheDocument()
	})

	test('does not show "deselect" button', () => {
		const deselectButton = screen.queryByTitle(/deselect/i)
		expect(deselectButton).not.toBeInTheDocument()
	})

	test('has an input field for search', () => {
		const inputField = screen.getByRole('combobox')
		expect(inputField).toBeInTheDocument()
	})

	test('allows to select sname options from database', () => {
		const yeomanSname = screen.getByText(
			/Yeoman \/ Formation \/ Saskatchewan/i
		)
		const aalenianSname = screen.getByText(/Aalenian \/ Stage \/ Global/i)
		expect(yeomanSname).toBeInTheDocument()
		expect(aalenianSname).toBeInTheDocument()
	})

	test('reflects the user input', async () => {
		const inputField = screen.getByRole('combobox')
		userEvent.type(inputField, 'Upper Ord')
		await screen.findByDisplayValue('Upper Ord')
	})

	test('allows to select an existing structured name', async () => {
		const inputField = screen.getByRole('combobox')
		userEvent.paste(inputField, dbSname1Formatted)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'SELECT_STRUCTURED_NAME',
			structured_name_id: dbStructuredName1.id,
		})
	})
})

/** This describe block uses real store instead of mocked one
 * to check that deselcct works as expected */
describe('When some existing structured names have been selected', () => {
	let store
	beforeEach(() => {
		jest.clearAllMocks()
		store = createStore(
			combineReducers({
				ref: refReducer,
				sname: snameReducer,
				rel: relReducer,
				map: mapReducer,
				names: nameReducer,
				selectedStructuredNames: selectedStructuredNamesReducer,
			}),
			applyMiddleware(thunk)
		)
		server.loadServerData.mockImplementation(k => [
			dbStructuredName1,
			dbStructuredName2,
		])
		store.dispatch(initMapvalues(initialMapState))
		store.dispatch(selectStructuredName(dbStructuredName1.id))
		render(
			<Provider store={store}>
				<SelectedStructuredNames />
			</Provider>
		)
	})

	test('shows selected sname on the selected snames list', () => {
		const selection = screen.getAllByText(
			/Yeoman \/ Formation \/ Saskatchewan/i
		)
		expect(selection).toHaveLength(2)
	})

	test('does not add duplicate selections to the selected snames list', async () => {
		const inputField = screen.getByRole('combobox')
		userEvent.paste(inputField, dbSname1Formatted)
		const selection = await screen.findAllByText(
			/Yeoman \/ Formation \/ Saskatchewan/i
		)
		expect(selection).toHaveLength(2)
	})

	test('shows "deselect" button', () => {
		const deselectButtons = screen.getAllByRole('button', {
			name: /Deselect/i,
		})
		expect(deselectButtons).toHaveLength(1)
	})

	test('allows to deselect the selected structured name', async () => {
		const deselectButton = screen.queryByTitle(/deselect/i)
		userEvent.click(deselectButton)
		const selection = await screen.findAllByText(
			/Yeoman \/ Formation \/ Saskatchewan/i
		)
		expect(selection).toHaveLength(1)
	})
})

describe('When selected structured names are dependent on relation', () => {
	let store
	beforeEach(() => {
		jest.clearAllMocks()
		store = mockStore({
			map: mapReducer(initialMapState, { type: 'INIT' }),
			rel: relReducer([], addRel(relation)),
			selectedStructuredNames: selectedStructuredNamesReducer(
				[],
				selectStructuredName(dbStructuredName1.id)
			),
		})
		store.dispatch = jest.fn()
		server.loadServerData.mockImplementation(k => [
			dbStructuredName1,
			dbStructuredName2,
		])
		render(
			<Provider store={store}>
				<SelectedStructuredNames />
			</Provider>
		)
	})

	test('does not allow to deselect the structured name', () => {
		const deselectButton = screen.queryByTitle(/deselect/i)
		userEvent.click(deselectButton)
		expect(store.dispatch).not.toHaveBeenCalled()
	})
})
