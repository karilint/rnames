import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { getByText } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { Relation } from '../Relation'
import { relReducer } from '../../store/relations/reducers'
import { mapReducer } from '../../store/map/reducers'
import { makeId } from '../../utilities'

const mockStore = configureStore([])

const dbStructuredName1 = {
	id: '{"type":"db_structured_name","value":1296}',
	name_id: '{"type":"db_name","value":1126}',
	location_id: '{"type":"db_location","value":70}',
	qualifier_id: '{"type":"db_qualifier","value":7}',
	reference_id: '{"type":"db_reference","value":0}',
	remarks: null,
}

const dbStructuredName2 = {
	id: '{"type":"db_structured_name","value":5031}',
	location_id: '{"type":"db_location","value":1}',
	name_id: '{"type":"db_name","value":4644}',
	qualifier_id: '{"type":"db_qualifier","value":5}',
	reference_id: '{"type":"db_reference","value":0}',
	remarks: null,
}

const relation = {
	id: makeId('relation'),
	name1: [dbStructuredName1.id],
	name2: [dbStructuredName2.id],
	belongs_to: 0,
	reference_id: -1,
}

const formattedName1 = 'Yeoman / Formation / Saskatchewan'
const formattedName2 = 'Aalenian / Stage / Global'

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

describe('When relation without inclusion rendered', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			rel: relReducer([], { type: 'INIT', rel: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Relation relation={relation} />
			</Provider>
		)
	})

	test('shows "swap" button', () => {
		const swapButton = screen.getByRole('button')
		expect(swapButton).toBeInTheDocument()
	})

	test('shows structured names forming a relation on the same row', () => {
		const relationRow = screen
			.getByText(`${formattedName1}`)
			.closest('.w3-row')
		const leftName = getByText(relationRow, `${formattedName1}`)
		const rightName = getByText(relationRow, `${formattedName2}`)
		const swapButton = getByText(relationRow, '↔')
		expect(leftName).toBeInTheDocument()
		expect(rightName).toBeInTheDocument()
		expect(swapButton).toBeInTheDocument()
	})

	test('swaps relations on "swap" button press', () => {
		const swapButton = screen.getByRole('button')
		userEvent.click(swapButton)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				...relation,
				name1: relation.name2,
				name2: relation.name1,
			},
		})
	})

	test('has "belongs to" checkbox', () => {
		const belongToCheckbox = screen.getByRole('checkbox')
		expect(belongToCheckbox).toBeInTheDocument()
	})

	test('creates inclusion on "belongs to" button click', () => {
		const belongToCheckbox = screen.getByRole('checkbox')
		userEvent.click(belongToCheckbox)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				...relation,
				belongs_to: 1,
			},
		})
	})
})

describe('When relation with inclusion rendered', () => {
	let store
	const relationWithInclusion = { ...relation, belongs_to: 1 }
	beforeEach(() => {
		store = mockStore({
			rel: relReducer([], { type: 'INIT', rel: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Relation relation={relationWithInclusion} />
			</Provider>
		)
	})

	test('removes inclusion on "belongs to" button click', () => {
		const belongToCheckbox = screen.getByRole('checkbox')
		userEvent.click(belongToCheckbox)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				...relation,
				belongs_to: 0,
			},
		})
	})
})
