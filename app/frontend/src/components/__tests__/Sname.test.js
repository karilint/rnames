import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { Sname } from '../Sname'
import { snameReducer } from '../../store/snames/reducers'
import { mapReducer } from '../../store/map/reducers'
import { relReducer } from '../../store/relations/reducers'
import { addSname } from '../../store/snames/actions'
import { addRel } from '../../store/relations/actions'

const mockStore = configureStore([])
const structured_name = {
	id: '{"type":"structured_name","value":1}',
	name_id: '{"type":"db_name","value":240}',
	location_id: '{"type":"db_location","value":37}',
	qualifier_id: '{"type":"db_qualifier","value":39}',
	reference_id: -1,
	remarks: '',
	save_with_reference_id: false,
}

const initialMapState = {
	'{"type":"db_name","value":240}': {
		id: '{"type":"db_name","value":240}',
		name: '1a',
	},
	'{"type":"db_location","value":37}': {
		id: '{"type":"db_location","value":37}',
		name: 'Alabama',
	},
	'{"type":"db_qualifier","value":39}': {
		id: '{"type":"db_qualifier","value":39}',
		level: 1,
		qualifier_name_id: '{"type":"db_qualifier_name","value":39}',
		stratigraphic_qualifier_id: 5,
	},
	'{"type":"db_qualifier_name","value":39}': {
		id: '{"type":"db_qualifier_name","value":39}',
		name: 'Bio_Ammonite',
	},
}

describe('Sname', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			map: mapReducer(initialMapState, addSname(structured_name)),
			sname: snameReducer([], addSname(structured_name)),
			rel: relReducer([], { type: 'INIT', rel: {} }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Sname
					sname={structured_name}
					canDeleteNotify={() => {}}
					nameNotify={() => {}}
					locationNotify={() => {}}
					setDeleteCreatedSname={() => {}}
				/>
				<button id='sname-button'>Add new structured name</button>
			</Provider>
		)
	})

	test('shows structured name information', () => {
		const name = screen.getByText(/1a/)
		const qualifier = screen.getByText(/Bio_Ammonite/)
		const location = screen.getByText(/Alabama/)
		expect(name).toBeInTheDocument()
		expect(qualifier).toBeInTheDocument()
		expect(location).toBeInTheDocument()
	})

	test('shows "delete" button', () => {
		const deleteButton = screen.getByRole('button', {
			name: /delete/i,
		})
		expect(deleteButton).toBeInTheDocument()
	})

	test('deletes sname on "delete" button click if no dependencies found and does not delete name or location from database', () => {
		const deleteButton = screen.getByRole('button', {
			name: /delete/i,
		})
		userEvent.click(deleteButton)
		expect(store.dispatch).toHaveBeenCalledTimes(2)
		expect(store.dispatch).toHaveBeenNthCalledWith(2, {
			sname: { ...structured_name },
			type: 'DELETE',
		})
	})
})

test('does not delete sname if there is a relation dependency', () => {
	const relation = {
		id: '{"type":"relation","value":3}',
		name1: '{"type":"structured_name","value":1}',
		name2: '{"type":"structured_name","value":2}',
		reference_id: -1,
		formattedName1: '1a / Bio_Ammonite / Alabama',
		formattedName2: '1b / Bio_Brachiopoda / Alaska',
	}
	const store = mockStore({
		map: mapReducer(initialMapState, {
			type: 'ADD',
			sname: structured_name,
		}),
		sname: snameReducer([], addSname(structured_name)),
		rel: relReducer([], addRel(relation)),
	})
	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<Sname
				sname={structured_name}
				canDeleteNotify={() => {}}
				nameNotify={() => {}}
				locationNotify={() => {}}
				setDeleteCreatedSname={() => {}}
			/>
			<button id='sname-button'>Add new structured name</button>
		</Provider>
	)

	const deleteButton = screen.getByRole('button', {
		name: /delete/i,
	})
	userEvent.click(deleteButton)
	expect(store.dispatch).not.toHaveBeenCalled()
})

test('deletes name created by user if no dependencies found', () => {
	const sname_with_new_name = {
		...structured_name,
		name_id: '{"type":"name","value":1}',
	}
	const store = mockStore({
		map: mapReducer(initialMapState, addSname(sname_with_new_name)),
		sname: snameReducer([], addSname(sname_with_new_name)),
		rel: relReducer([], { type: 'INIT', rel: {} }),
	})
	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<Sname
				sname={sname_with_new_name}
				canDeleteNotify={() => {}}
				nameNotify={() => {}}
				locationNotify={() => {}}
				setDeleteCreatedSname={() => {}}
			/>
			<button id='sname-button'>Add new structured name</button>
		</Provider>
	)

	const deleteButton = screen.getByRole('button', {
		name: /delete/i,
	})
	userEvent.click(deleteButton)
	expect(store.dispatch).toHaveBeenCalledTimes(3)
	expect(store.dispatch).toHaveBeenNthCalledWith(1, {
		nameId: '{"type":"name","value":1}',
		name: {},
		type: 'DELETE_NAME',
	})
})

test('deletes location created by user if no dependencies found', () => {
	const sname_with_new_location = {
		...structured_name,
		location_id: '{"type":"location","value":1}',
	}
	const store = mockStore({
		map: mapReducer(initialMapState, addSname(sname_with_new_location)),
		sname: snameReducer([], addSname(sname_with_new_location)),
		rel: relReducer([], { type: 'INIT', rel: {} }),
	})
	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<Sname
				sname={sname_with_new_location}
				canDeleteNotify={() => {}}
				nameNotify={() => {}}
				locationNotify={() => {}}
				setDeleteCreatedSname={() => {}}
			/>
			<button id='sname-button'>Add new structured name</button>
		</Provider>
	)

	const deleteButton = screen.getByRole('button', {
		name: /delete/i,
	})
	userEvent.click(deleteButton)
	expect(store.dispatch).toHaveBeenCalledTimes(3)
	expect(store.dispatch).toHaveBeenNthCalledWith(1, {
		nameId: '{"type":"location","value":1}',
		name: {},
		type: 'DELETE_NAME',
	})
})

test('deletes both name and location created by user if no dependencies found', () => {
	const sname_with_new_name_and_location = {
		...structured_name,
		name_id: '{"type":"name","value":1}',
		location_id: '{"type":"location","value":2}',
	}
	const store = mockStore({
		map: mapReducer(
			initialMapState,
			addSname(sname_with_new_name_and_location)
		),
		sname: snameReducer([], addSname(sname_with_new_name_and_location)),
		rel: relReducer([], { type: 'INIT', rel: {} }),
	})
	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<Sname
				sname={sname_with_new_name_and_location}
				canDeleteNotify={() => {}}
				nameNotify={() => {}}
				locationNotify={() => {}}
				setDeleteCreatedSname={() => {}}
			/>
			<button id='sname-button'>Add new structured name</button>
		</Provider>
	)

	const deleteButton = screen.getByRole('button', {
		name: /delete/i,
	})
	userEvent.click(deleteButton)
	expect(store.dispatch).toHaveBeenCalledTimes(4)
	expect(store.dispatch).toHaveBeenNthCalledWith(1, {
		nameId: '{"type":"name","value":1}',
		name: {},
		type: 'DELETE_NAME',
	})
	expect(store.dispatch).toHaveBeenNthCalledWith(2, {
		nameId: '{"type":"location","value":2}',
		name: {},
		type: 'DELETE_NAME',
	})
})

test('does not delete name created by user if dependency found', () => {
	const sname_with_new_name = {
		...structured_name,
		name_id: '{"type":"name","value":1}',
	}
	const store = mockStore({
		map: mapReducer(initialMapState, addSname(sname_with_new_name)),
		sname: snameReducer(
			[
				{
					id: '{"type":"structured_name","value":6}',
					name_id: '{"type":"name","value":1}',
					location_id: '{"type":"db_location","value":56}',
					qualifier_id: '{"type":"db_qualifier","value":36}',
					reference_id: -1,
					remarks: '',
					save_with_reference_id: false,
				},
			],
			addSname(sname_with_new_name)
		),
		rel: relReducer([], { type: 'INIT', rel: {} }),
	})
	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<Sname
				sname={sname_with_new_name}
				canDeleteNotify={() => {}}
				nameNotify={() => {}}
				locationNotify={() => {}}
				setDeleteCreatedSname={() => {}}
			/>
			<button id='sname-button'>Add new structured name</button>
		</Provider>
	)

	const deleteButton = screen.getByRole('button', {
		name: /delete/i,
	})
	userEvent.click(deleteButton)
	expect(store.dispatch).toHaveBeenCalledTimes(2)
	expect(store.dispatch).not.toHaveBeenCalledWith({
		nameId: '{"type":"name","value":1}',
		name: {},
		type: 'DELETE_NAME',
	})
})

test('does not delete location created by user if dependency found', () => {
	const sname_with_new_location = {
		...structured_name,
		location_id: '{"type":"location","value":1}',
	}
	const store = mockStore({
		map: mapReducer(initialMapState, addSname(sname_with_new_location)),
		sname: snameReducer(
			[
				{
					id: '{"type":"structured_name","value":6}',
					name_id: '{"type":"db_name","value":240}',
					location_id: '{"type":"location","value":1}',
					qualifier_id: '{"type":"db_qualifier","value":36}',
					reference_id: -1,
					remarks: '',
					save_with_reference_id: false,
				},
			],
			addSname(sname_with_new_location)
		),
		rel: relReducer([], { type: 'INIT', rel: {} }),
	})
	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<Sname
				sname={sname_with_new_location}
				canDeleteNotify={() => {}}
				nameNotify={() => {}}
				locationNotify={() => {}}
				setDeleteCreatedSname={() => {}}
			/>
			<button id='sname-button'>Add new structured name</button>
		</Provider>
	)

	const deleteButton = screen.getByRole('button', {
		name: /delete/i,
	})
	userEvent.click(deleteButton)
	expect(store.dispatch).toHaveBeenCalledTimes(2)
	expect(store.dispatch).not.toHaveBeenCalledWith({
		nameId: '{"type":"location","value":1}',
		name: {},
		type: 'DELETE_NAME',
	})
})
