import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { BelongsToSelector } from '../BelongsToSelector'
import { makeId } from '../../utilities'

const mockStore = configureStore([])

const activeButtonClass = 'w3-grey'

const belongsToSelectorInclusionButtonsTestIds = {
	noInclusion: 'noInclusion-test-id',
	rightToLeft: 'rightToLeft-test-id',
	leftToRight: 'leftToRight-test-id',
}

const sname1Id = '{"type":"structured_name","value":1}'
const sname2Id = '{"type":"db_structured_name","value":4422}'
const nonInclusiveRelation = {
	id: makeId('relation'),
	name1: sname1Id,
	name2: sname2Id,
	belongs_to: 0,
	reference_id: -1,
}

describe('When pair of structured names is added, but no relations formed', () => {
	let store
	beforeEach(() => {
		store = mockStore()
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<BelongsToSelector idA={sname1Id} idB={sname2Id} />
			</Provider>
		)
	})

	test('shows three buttons for different inclusion options', () => {
		const rightToLeft = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		const noInclusion = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		const leftToRight = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		expect(rightToLeft).toBeInTheDocument()
		expect(noInclusion).toBeInTheDocument()
		expect(leftToRight).toBeInTheDocument()
	})

	test('no option is rendered as selected', () => {
		const rightToLeft = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		const noInclusion = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		const leftToRight = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		expect(rightToLeft).not.toHaveClass(`${activeButtonClass}`)
		expect(noInclusion).not.toHaveClass(`${activeButtonClass}`)
		expect(leftToRight).not.toHaveClass(`${activeButtonClass}`)
	})

	test('creates new relation and rightToLeft inclusion on "rightToLeft" button click', () => {
		const rightToLeft = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		userEvent.click(rightToLeft)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'ADD',
			rel: {
				id: expect.anything(),
				name1: sname1Id,
				name2: sname2Id,
				belongs_to: 1,
				reference_id: -1,
			},
		})
	})

	test('creates new relation with no inclusion on "noInclusion" button click', () => {
		const noInclusion = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		userEvent.click(noInclusion)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'ADD',
			rel: {
				id: expect.anything(),
				name1: sname1Id,
				name2: sname2Id,
				belongs_to: 0,
				reference_id: -1,
			},
		})
	})

	test('creates new relation and leftToRight inclusion on "leftToRight" button click', () => {
		const leftToRight = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(leftToRight)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'ADD',
			rel: {
				id: expect.anything(),
				name1: sname2Id,
				name2: sname1Id,
				belongs_to: 1,
				reference_id: -1,
			},
		})
	})
})

describe('When pair of structured names with non inclusive relation added', () => {
	let store
	beforeEach(() => {
		store = mockStore()
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<BelongsToSelector
					idA={sname1Id}
					idB={sname2Id}
					relation={nonInclusiveRelation}
				/>
			</Provider>
		)
	})

	test('shows "noInclusion" button as selected', () => {
		const noInclusion = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		expect(noInclusion).toHaveClass(`${activeButtonClass}`)
	})

	test('updates relation and creates rightToLeft inclusion on "rightToLeft" button click', () => {
		const rightToLeft = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		userEvent.click(rightToLeft)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				id: expect.anything(),
				name1: sname1Id,
				name2: sname2Id,
				belongs_to: 1,
				reference_id: -1,
			},
		})
	})

	test('updates relation and creates leftToRight inclusion on "leftToRight" button click', () => {
		const leftToRight = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(leftToRight)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				id: expect.anything(),
				name1: sname2Id,
				name2: sname1Id,
				belongs_to: 1,
				reference_id: -1,
			},
		})
	})
})

describe('When pair of structured names with inclusive relation added and sname1 is on the left side', () => {
	const inclusiveRelation = { ...nonInclusiveRelation, belongs_to: 1 }
	let store
	beforeEach(() => {
		store = mockStore()
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<BelongsToSelector
					idA={sname1Id}
					idB={sname2Id}
					relation={inclusiveRelation}
				/>
			</Provider>
		)
	})

	test('shows "rightToLeft" button as selected', () => {
		const rightToLeft = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		expect(rightToLeft).toHaveClass(`${activeButtonClass}`)
	})

	test('updates relation and creates leftToRight inclusion on "leftToRight" button click', () => {
		const leftToRight = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(leftToRight)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				id: expect.anything(),
				name1: sname2Id,
				name2: sname1Id,
				belongs_to: 1,
				reference_id: -1,
			},
		})
	})

	test('updates relation and removes inclusion on "noInclusion" button click', () => {
		const noInclusion = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		userEvent.click(noInclusion)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				id: expect.anything(),
				name1: sname1Id,
				name2: sname2Id,
				belongs_to: 0,
				reference_id: -1,
			},
		})
	})
})

describe('When pair of structured names with inclusive relation added and sname1 is on the right side', () => {
	const inclusiveRelation = {
		...nonInclusiveRelation,
		belongs_to: 1,
		name1: sname2Id,
		name2: sname1Id,
	}
	let store
	beforeEach(() => {
		store = mockStore()
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<BelongsToSelector
					idA={sname1Id}
					idB={sname2Id}
					relation={inclusiveRelation}
				/>
			</Provider>
		)
	})

	test('shows "leftToRight" button as selected', () => {
		const leftToRight = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		expect(leftToRight).toHaveClass(`${activeButtonClass}`)
	})

	test('updates relation and creates rightToLeft inclusion on "rightToLeft" button click', () => {
		const rightToLeft = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		userEvent.click(rightToLeft)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				id: expect.anything(),
				name1: sname1Id,
				name2: sname2Id,
				belongs_to: 1,
				reference_id: -1,
			},
		})
	})

	test('updates relation and removes inclusion on "noInclusion" button click', () => {
		const noInclusion = screen.getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		userEvent.click(noInclusion)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'UPDATE',
			rel: {
				id: expect.anything(),
				name1: sname2Id,
				name2: sname1Id,
				belongs_to: 0,
				reference_id: -1,
			},
		})
	})
})
