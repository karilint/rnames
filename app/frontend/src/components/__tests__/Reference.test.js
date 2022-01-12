import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import { Reference } from '../Reference'
import { Provider } from 'react-redux'
import { refReducer } from '../../store/references/reducers'

const mockStore = configureStore([])

const ref = {
	firstAuthor: 'Úna C. Farrell',
	year: 2009,
	title: "Beyond Beecher's Trilobite Bed: Widespread pyritization of soft tissues in the Late Ordovician Taconic foreland basin",
	doi: '10.1130/g30177a.1',
	link: 'https://pubs.geoscienceworld.org/gsa/geology/article-abstract/37/10/907/103864/Beyond-Beecher-s-Trilobite-Bed-Widespread',
	exists: false,
	queried: true,
	edit: false,
	id: '{"type":"reference","value":1}',
}

describe('Reference', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer,
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<Reference reference={ref} showNewReferenceForm={() => {}} />
			</Provider>
		)
	})

	test('has one button', () => {
		expect(screen.getAllByRole('button')).toHaveLength(1)
	})

	test('shows author correctly', () => {
		const firstAuthor = screen.getByText(ref.firstAuthor, { exact: false })
		expect(firstAuthor).toBeInTheDocument()
	})

	test('shows year correctly', () => {
		const year = screen.getByText(ref.year, { exact: false })
		expect(year).toBeInTheDocument()
	})

	test('shows title correctly', () => {
		const title = screen.getByText(ref.title, { exact: false })
		expect(title).toBeInTheDocument()
	})

	test('shows doi correctly', () => {
		const doi = screen.getByText(ref.doi, { exact: false })
		expect(doi).toBeInTheDocument()
	})

	test('shows link correctly', () => {
		const link = screen.getByText(ref.link, { exact: false })
		expect(link).toBeInTheDocument()
	})

	test('sets reference to edit state on edit button click', async () => {
		const editButton = screen.getByRole('button')
		userEvent.click(editButton)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			ref: { ...ref, edit: true },
			type: 'UPDATE',
		})
	})
})
