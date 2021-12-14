import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import axios from 'axios'
import { Submit } from '../Submit'
import { Provider } from 'react-redux'
import { refReducer } from '../../store/references/reducers'
import { snameReducer } from '../../store/snames/reducers'
import { relReducer } from '../../store/relations/reducers'
import { nameReducer } from '../../store/names/reducers'
import { addRef } from '../../store/references/actions'
import { addSname } from '../../store/snames/actions'
import { addRel } from '../../store/relations/actions'
import { makeId } from '../../utilities'

jest.mock('axios')
const mockStore = configureStore([])

const reference = {
	firstAuthor: 'Úna C. Farrell',
	year: 2009,
	title: "Beyond Beecher's Trilobite Bed: Widespread pyritization of soft tissues in the Late Ordovician Taconic foreland basin",
	doi: '10.1130/g30177a.1',
	link: 'https://pubs.geoscienceworld.org/gsa/geology/article-abstract/37/10/907/103864/Beyond-Beecher-s-Trilobite-Bed-Widespread',
	exists: false,
	queried: true,
	edit: false,
	id: makeId('reference'),
}

const structuredName = {
	id: makeId('structured_name'),
	name_id: makeId('db_name'),
	location_id: makeId('db_location'),
	qualifier_id: makeId('db_qualifier'),
	reference_id: -1,
	remarks: '',
	save_with_reference_id: true,
}

const relation = {
	id: makeId('relation'),
	name1: structuredName.id,
	name2: makeId('structured_name'),
	reference_id: -1,
}

describe('When no reference provided', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer([], { type: 'INIT', ref: {} }),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			rel: relReducer([], { type: 'INIT', rel: {} }),
			names: nameReducer([], { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Submit />
			</Provider>
		)
	})
	test('has button for submitting information', () => {
		const submitButton = screen.getByRole('button', { name: /submit/i })
		expect(submitButton).toBeInTheDocument()
	})

	test('does not allow to make submit', async () => {
		const submitButton = screen.getByRole('button', { name: /submit/i })
		userEvent.click(submitButton)
		await screen.findByText(/Please add reference before submitting/i)
	})
})

describe('When reference provided', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer([], addRef(reference)),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			rel: relReducer([], { type: 'INIT', rel: {} }),
			names: nameReducer([], { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Submit />
			</Provider>
		)
	})
	/**
	 * Structured names can be chosen from the database (no requirement to add new ones before submitting),
	 * but it is necessary to choose or add structured names before creating relations.
	 */
	test('does not allow to make submit if no relations provided', async () => {
		const submitButton = screen.getByRole('button', { name: /submit/i })
		userEvent.click(submitButton)
		await screen.findByText(
			/Please add structured names and relations before submitting/i
		)
	})
})

describe('When provided reference is in edit mode', () => {
	const referenceInEditMode = { ...reference, edit: true }
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer([], addRef(referenceInEditMode)),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			rel: relReducer([], { type: 'INIT', rel: {} }),
			names: nameReducer([], { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Submit />
			</Provider>
		)
	})
	test('does not allow to make submit', async () => {
		const submitButton = screen.getByRole('button', { name: /submit/i })
		userEvent.click(submitButton)
		await screen.findByText(
			/Please save changes made in reference before submitting/i
		)
	})
})

describe('When correct reference information provided', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer([], addRef(reference)),
			sname: snameReducer([], addSname(structuredName)),
			rel: relReducer([], addRel(relation)),
			names: nameReducer([], { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Submit />
				<input
					name='csrfmiddlewaretoken'
					type='hidden'
					value='iuWgmrwb9bCCnrgyBplY52qEP8Be1USdh1MPGjpwiwi7OOgLv6SuXC4gwh5IWENn'
				></input>
			</Provider>
		)
	})

	test('submits data to the server', async () => {
		const submitButton = screen.getByRole('button', { name: /submit/i })
		axios.mockImplementationOnce(() => Promise.resolve(true))
		userEvent.click(submitButton)
		expect(axios).toHaveBeenCalledTimes(1)
		expect(axios).toHaveBeenCalledWith({
			data: {
				names: [],
				reference: {
					doi: '10.1130/g30177a.1',
					edit: false,
					exists: false,
					firstAuthor: 'Úna C. Farrell',
					id: { type: 'reference', value: expect.anything() },
					link: 'https://pubs.geoscienceworld.org/gsa/geology/article-abstract/37/10/907/103864/Beyond-Beecher-s-Trilobite-Bed-Widespread',
					queried: true,
					title: "Beyond Beecher's Trilobite Bed: Widespread pyritization of soft tissues in the Late Ordovician Taconic foreland basin",
					year: 2009,
				},
				relations: [
					{
						id: { type: 'relation', value: expect.anything() },
						name1: {
							type: 'structured_name',
							value: expect.anything(),
						},
						name2: {
							type: 'structured_name',
							value: expect.anything(),
						},
						reference_id: -1,
					},
				],
				structured_names: [
					{
						id: {
							type: 'structured_name',
							value: expect.anything(),
						},
						location_id: {
							type: 'db_location',
							value: expect.anything(),
						},
						name_id: {
							type: 'db_name',
							value: expect.anything(),
						},
						qualifier_id: {
							type: 'db_qualifier',
							value: expect.anything(),
						},
						reference_id: -1,
						remarks: '',
						save_with_reference_id: true,
					},
				],
			},
			headers: {
				'X-CSRFToken':
					'iuWgmrwb9bCCnrgyBplY52qEP8Be1USdh1MPGjpwiwi7OOgLv6SuXC4gwh5IWENn',
			},
			method: 'POST',
			url: '/wizard_submit',
		})
	})
})
