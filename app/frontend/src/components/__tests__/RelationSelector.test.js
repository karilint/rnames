import React from 'react'
import { createStore, combineReducers, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen, within } from '@testing-library/react'
import { getByText } from '@testing-library/dom'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import { Provider } from 'react-redux'
import { refReducer } from '../../store/references/reducers'
import { snameReducer } from '../../store/snames/reducers'
import { relReducer } from '../../store/relations/reducers'
import { selectedStructuredNamesReducer } from '../../store/selected_structured_names/reducers'
import { makeId } from '../../utilities'
import { mapReducer } from '../../store/map/reducers'
import { nameReducer } from '../../store/names/reducers'
import { initMapvalues } from '../../store/map/actions'
import { RelationSelector } from '../RelationSelector'
import { selectStructuredName } from '../../store/selected_structured_names/actions'
import { addSname } from '../../store/snames/actions'
import { addRel } from '../../store/relations/actions'

const activeButtonClass = 'w3-grey'

const belongsToSelectorInclusionButtonsTestIds = {
	noInclusion: 'noInclusion-test-id',
	rightToLeft: 'rightToLeft-test-id',
	leftToRight: 'leftToRight-test-id',
}

const relationSelectorSidesTestIds = {
	left: 'relselector-left-test-id',
	right: 'relselector-right-test-id',
}

const dbStructuredName1 = {
	id: '{"type":"db_structured_name","value":1296}',
	name_id: '{"type":"db_name","value":1126}',
	location_id: '{"type":"db_location","value":70}',
	qualifier_id: '{"type":"db_qualifier","value":7}',
	reference_id: '{"type":"db_reference","value":0}',
	remarks: null,
}

const dbSname1Formatted = 'Yeoman / Formation / Saskatchewan'

const dbStructuredName2 = {
	id: '{"type":"db_structured_name","value":5031}',
	location_id: '{"type":"db_location","value":1}',
	name_id: '{"type":"db_name","value":4644}',
	qualifier_id: '{"type":"db_qualifier","value":5}',
	reference_id: '{"type":"db_reference","value":0}',
	remarks: null,
}

const dbSname2Formatted = 'Aalenian / Stage / Global'

const structuredName = {
	id: '{"type":"structured_name","value":1}',
	name_id: '{"type":"db_name","value":3437}',
	location_id: '{"type":"db_location","value":9}',
	qualifier_id: '{"type":"db_qualifier","value":3}',
	reference_id: -1,
	remarks: '',
	save_with_reference_id: false,
}

const snameFormatted = 'Abercwmeiddaw / Epoch / Korea'

const relation = {
	id: makeId('relation'),
	name1: dbStructuredName1.id,
	name2: structuredName.id,
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
	[structuredName.name_id]: {
		id: [structuredName.name_id],
		name: 'Abercwmeiddaw',
	},
	[structuredName.location_id]: {
		id: [structuredName.location_id],
		name: 'Korea',
	},
	[structuredName.qualifier_id]: {
		id: [structuredName.qualifier_id],
		level: 4,
		qualifier_name_id: '{"type":"db_qualifier_name","value":3}',
		stratigraphic_qualifier_id: 1,
	},
	'{"type":"db_qualifier_name","value":3}': {
		id: '{"type":"db_qualifier_name","value":3}',
		name: 'Epoch',
	},
}

/** RelationSelector tests use real store instead of the mocked one. */

describe('When some structured names have been selected, but no relations formed, RelationSelector', () => {
	let store
	beforeEach(() => {
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
		render(
			<Provider store={store}>
				<RelationSelector />
			</Provider>
		)
		store.dispatch(initMapvalues(initialMapState))
		store.dispatch(addSname(structuredName))
		store.dispatch(selectStructuredName(structuredName.id))
		store.dispatch(selectStructuredName(dbStructuredName2.id))
		store.dispatch(selectStructuredName(dbStructuredName1.id))
	})

	test('has "Create relations" heading', () => {
		const createRelationsHeading = screen.getByRole('heading', {
			name: /Create relations/i,
		})
		expect(createRelationsHeading).toBeInTheDocument()
	})

	test('has "Relations" heading', () => {
		const relationsHeading = screen.getByRole('heading', {
			name: /^Relations/i,
		})
		expect(relationsHeading).toBeInTheDocument()
	})

	test('on the left side has all the selected structured names as options', () => {
		const relationSelectorOnTheLeft = screen.getByTestId(
			relationSelectorSidesTestIds.left
		)
		const options = [dbSname1Formatted, dbSname2Formatted, snameFormatted]

		expect(relationSelectorOnTheLeft.childNodes).toHaveLength(3)
		relationSelectorOnTheLeft.childNodes.forEach(childNode => {
			expect(options).toContain(childNode.innerHTML)
		})
	})

	test('on the right side has all the selected structured names as options except the primary one', () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const options = [dbSname1Formatted, dbSname2Formatted]
		expect(relationSelectorOnTheRight.childNodes).toHaveLength(2)
		relationSelectorOnTheRight.childNodes.forEach(childNode => {
			expect(options).toContain(childNode.childNodes[3].innerHTML)
		})
	})

	test('does not render any relations under "Relations" heading', async () => {
		const relationsList = screen.getByTestId('active-relations-list')
		expect(relationsList.childNodes.length).toEqual(0)
	})

	test('shows correct labels for relations list table columns', () => {
		const heading = screen.getByTestId('active-relations-list').parentNode
			.childNodes[0]
		const labels = [
			'Structured Name 1',
			'Swap',
			'Belongs to',
			'Structured Name 2',
		]

		labels.forEach(label => {
			const domLabel = getByText(heading, label)
			expect(domLabel).toBeInTheDocument()
		})
	})

	test('selects "noInclusion" as deafult when user creates relation', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)

		const nameOnRight = getByText(
			relationSelectorOnTheRight,
			dbSname1Formatted
		)
		userEvent.click(nameOnRight)

		const firstOption = nameOnRight.parentNode
		const noInclusionButton = await within(firstOption).findByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		const rightToLeftButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		const leftToRightButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		expect(noInclusionButton).toHaveClass(`${activeButtonClass}`)
		expect(rightToLeftButton).not.toHaveClass(`${activeButtonClass}`)
		expect(leftToRightButton).not.toHaveClass(`${activeButtonClass}`)
	})

	test('allows to select "rightToLeft" inclusion when creating relation', () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const rightToLeftButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		const noInclusionButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		const leftToRightButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(rightToLeftButton)
		expect(rightToLeftButton).toHaveClass(`${activeButtonClass}`)
		expect(leftToRightButton).not.toHaveClass(`${activeButtonClass}`)
		expect(noInclusionButton).not.toHaveClass(`${activeButtonClass}`)
	})

	test('allows to select "leftToRight" inclusion when creating relation', () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const rightToLeftButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		const noInclusionButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		const leftToRightButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(leftToRightButton)
		expect(leftToRightButton).toHaveClass(`${activeButtonClass}`)
		expect(rightToLeftButton).not.toHaveClass(`${activeButtonClass}`)
		expect(noInclusionButton).not.toHaveClass(`${activeButtonClass}`)
	})

	test('allows to select "noInclusion" as option when creating relation', () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const rightToLeftButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		const noInclusionButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.noInclusion
		)
		const leftToRightButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(noInclusionButton)
		expect(noInclusionButton).toHaveClass(`${activeButtonClass}`)
		expect(rightToLeftButton).not.toHaveClass(`${activeButtonClass}`)
		expect(leftToRightButton).not.toHaveClass(`${activeButtonClass}`)
	})

	test('adds relation to relations list after creation', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0].lastChild
		const firstOptionsFormattedName = firstOption.innerHTML
		userEvent.click(firstOption)
		const relationsList = screen.getByTestId('active-relations-list')
		await within(relationsList).findByText(firstOptionsFormattedName)
	})

	test('does not check "Belongs to" checkbox if relation does not have inclusion', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0].lastChild
		userEvent.click(firstOption)
		const checkbox = await screen.findByRole('checkbox')
		expect(checkbox).not.toBeChecked()
	})

	test('checks "Belongs to" checkbox if relation has rightToLeft inclusion', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const rightToLeftButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		userEvent.click(rightToLeftButton)
		const checkbox = await screen.findByRole('checkbox')
		expect(checkbox).toBeChecked()
	})

	test('checks "Belongs to" checkbox if relation has leftToRight inclusion', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const leftToRightButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(leftToRightButton)
		const checkbox = await screen.findByRole('checkbox')
		expect(checkbox).toBeChecked()
	})

	test('shows primary sname on the left side of relations list when "rightToLeft" inclusion selected', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const rightToLeftButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.rightToLeft
		)
		userEvent.click(rightToLeftButton)
		const relation = screen.getByTestId('active-relations-list')
			.childNodes[0]
		expect(
			getByText(relation.childNodes[0], snameFormatted)
		).toBeInTheDocument()
	})

	test('shows primary sname on the right side of relations list when "leftToRight" inclusion selected', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const firstOption = relationSelectorOnTheRight.childNodes[0]
		const leftToRightButton = within(firstOption).getByTestId(
			belongsToSelectorInclusionButtonsTestIds.leftToRight
		)
		userEvent.click(leftToRightButton)
		const relation = screen.getByTestId('active-relations-list')
			.childNodes[0]
		expect(
			getByText(relation.childNodes[0], dbSname1Formatted)
		).toBeInTheDocument()
		expect(
			getByText(relation.childNodes[3], snameFormatted)
		).toBeInTheDocument()
	})
})

describe('When some structured names have been selected and relations formed, RelationSelector', () => {
	let store
	beforeEach(() => {
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

		render(
			<Provider store={store}>
				<RelationSelector />
			</Provider>
		)
		store.dispatch(initMapvalues(initialMapState))
		store.dispatch(addSname(structuredName))
		store.dispatch(selectStructuredName(structuredName.id))
		store.dispatch(selectStructuredName(dbStructuredName2.id))
		store.dispatch(selectStructuredName(dbStructuredName1.id))
		store.dispatch(addRel(relation))
	})

	test('shows correct structured names as selected', () => {
		const relationSelectorOnTheLeft = screen.getByTestId(
			relationSelectorSidesTestIds.left
		)
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const selectedSname1 = within(relationSelectorOnTheLeft).getByText(
			snameFormatted
		)
		const selectedSname2 = within(relationSelectorOnTheRight).getByText(
			dbSname1Formatted
		)

		expect(selectedSname1).toHaveClass(`${activeButtonClass}`)
		expect(selectedSname2).toHaveClass(`${activeButtonClass}`)
	})

	test('allows to remove the selection', () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const selectedSname2 = within(relationSelectorOnTheRight).getByText(
			dbSname1Formatted
		).parentNode
		userEvent.click(selectedSname2)
		expect(selectedSname2).not.toHaveClass(`${activeButtonClass}`)
	})

	test('removes the relation from relation list after deselcting structured name', async () => {
		const relationSelectorOnTheRight = screen.getByTestId(
			relationSelectorSidesTestIds.right
		)
		const selectedSname2 = within(relationSelectorOnTheRight).getByText(
			dbSname1Formatted
		)
		userEvent.click(selectedSname2)
		const relationsList = screen.getByTestId('active-relations-list')
		expect(relationsList.childNodes.length).toEqual(0)
	})
})
