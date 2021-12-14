import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { SnameForm } from '../SnameForm'
import { snameReducer } from '../../store/snames/reducers'
import { refReducer } from '../../store/references/reducers'
import { mapReducer } from '../../store/map/reducers'
import { nameReducer } from '../../store/names/reducers'
import * as utilities from '../../utilities.js'
import { addRef } from '../../store/references/actions'
import { addName } from '../../store/names/actions'

const mockStore = configureStore([])
jest.spyOn(utilities, 'findDuplicateStructuredNames')

const reference = {
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

const initialMapState = {
	'{"type":"db_name","value":240}': {
		id: '{"type":"db_name","value":240}',
		name: '1a',
	},
	'{"type":"db_name","value":241}': {
		id: '{"type":"db_name","value":241}',
		name: '1b',
	},
	'{"type":"db_name","value":3144}': {
		id: '{"type":"db_name","value":3144}',
		name: '452.52',
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
	'{"type":"db_qualifier","value":36}': {
		id: '{"type":"db_qualifier","value":36}',
		level: 1,
		qualifier_name_id: '{"type":"db_qualifier_name","value":36}',
		stratigraphic_qualifier_id: 5,
	},
	'{"type":"db_qualifier_name","value":39}': {
		id: '{"type":"db_qualifier_name","value":39}',
		name: 'Bio_Ammonite',
	},
	'{"type":"db_qualifier_name","value":36}': {
		id: '{"type":"db_qualifier_name","value":36}',
		name: 'Bio_Brachiopoda',
	},
}

describe('When reference provided, SnameForm', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer([], addRef(reference)),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
			names: nameReducer([], { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<SnameForm
					displaySnameForm='block'
					showNewSnameForm={() => {}}
					newSnameButtonIsDisabled={true}
					setNewSnameButtonIsDisabled={() => {}}
					setFocusOnSnameButton={() => {}}
					displayRefForm='none'
					deleteCreatedSname={false}
					setDeleteCreatedSname={() => {}}
				/>
			</Provider>
		)
		utilities.findDuplicateStructuredNames.mockImplementation(
			(sname, structuredNames) => []
		)
	})
	test('has button for saving sname', () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		expect(saveButton).toBeInTheDocument()
	})

	test('has three fields for choosing name, qualifier and location', () => {
		const inputFields = screen.getAllByRole('combobox')
		expect(inputFields).toHaveLength(3)
	})

	test('has option to save sname with reference', () => {
		const saveWithReferenceCheckbox = screen.getByRole('checkbox')
		expect(saveWithReferenceCheckbox).toBeInTheDocument()
	})

	test('renders options correctly', () => {
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption =
			nameDropdown.querySelector('option[value="1b"]')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown.querySelector(
			'option[value="Bio_Brachiopoda"]'
		)
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown.querySelector(
			'option[value="Alabama"]'
		)
		expect(nameDropdown.childNodes).toHaveLength(3)
		expect(qualifierDropdown.childNodes).toHaveLength(2)
		expect(locationDropdown.childNodes).toHaveLength(1)
		expect(selectedNameOption).not.toBeNull()
		expect(selectedQualifierOption).not.toBeNull()
		expect(selectedLocationOption).not.toBeNull()
	})

	test('creates a new structured name on save', () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveButton)
		expect(store.dispatch).toHaveBeenCalledTimes(2)
		expect(store.dispatch).toHaveBeenNthCalledWith(1, {
			type: 'ADD',
			sname: {
				id: expect.anything(),
				name_id: '{"type":"db_name","value":241}',
				location_id: '{"type":"db_location","value":37}',
				qualifier_id: '{"type":"db_qualifier","value":36}',
				reference_id: -1,
				remarks: '',
				save_with_reference_id: false,
			},
		})
	})

	test('allows user to create new name on save', () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, 'newName')
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveButton)
		expect(store.dispatch).toHaveBeenCalledTimes(3)
		expect(store.dispatch).toHaveBeenNthCalledWith(1, {
			type: 'ADD_NAME',
			name: {
				id: expect.anything(),
				name: 'newName',
				variant: 'name',
			},
		})
		expect(store.dispatch).toHaveBeenNthCalledWith(2, {
			type: 'ADD',
			sname: {
				id: expect.anything(),
				name_id: expect.anything(),
				location_id: '{"type":"db_location","value":37}',
				qualifier_id: '{"type":"db_qualifier","value":36}',
				reference_id: -1,
				remarks: '',
				save_with_reference_id: false,
			},
		})
	})

	test('does not allow user to create new qualifier on save', async () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, 'newQualifier')
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveButton)
		const qualifierError = await screen.findByText(
			/Choose a qualifier from the dropdown menu/i
		)
		expect(store.dispatch).not.toHaveBeenCalled()
		expect(qualifierError).toBeInTheDocument()
	})

	test('allows user to create new location on save', () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, 'newLocation')
		userEvent.click(saveButton)
		expect(store.dispatch).toHaveBeenCalledTimes(3)
		expect(store.dispatch).toHaveBeenNthCalledWith(1, {
			type: 'ADD_NAME',
			name: {
				id: expect.anything(),
				name: 'newLocation',
				variant: 'location',
			},
		})

		expect(store.dispatch).toHaveBeenNthCalledWith(2, {
			type: 'ADD',
			sname: {
				id: expect.anything(),
				name_id: '{"type":"db_name","value":241}',
				location_id: expect.anything(),
				qualifier_id: '{"type":"db_qualifier","value":36}',
				reference_id: -1,
				remarks: '',
				save_with_reference_id: false,
			},
		})
	})

	test('allows user to save sname with reference id', () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		const saveWithReferenceCheckbox = screen.getByRole('checkbox')
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveWithReferenceCheckbox)
		userEvent.click(saveButton)
		expect(store.dispatch).toHaveBeenCalledTimes(2)
		expect(store.dispatch).toHaveBeenNthCalledWith(1, {
			type: 'ADD',
			sname: {
				id: expect.anything(),
				name_id: '{"type":"db_name","value":241}',
				location_id: '{"type":"db_location","value":37}',
				qualifier_id: '{"type":"db_qualifier","value":36}',
				reference_id: -1,
				remarks: '',
				save_with_reference_id: true,
			},
		})
	})

	test('allows user to enter remarks', () => {
		const remarksText = 'hello world'

		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)

		const remarksInput = screen.getAllByRole('textbox')[0]
		userEvent.type(remarksInput, remarksText)

		userEvent.click(saveButton)
		expect(store.dispatch).toHaveBeenCalledTimes(2)
		expect(store.dispatch).toHaveBeenNthCalledWith(1, {
			type: 'ADD',
			sname: {
				id: expect.anything(),
				name_id: '{"type":"db_name","value":241}',
				location_id: '{"type":"db_location","value":37}',
				qualifier_id: '{"type":"db_qualifier","value":36}',
				reference_id: -1,
				remarks: remarksText,
				save_with_reference_id: false,
			},
		})
	})
})

describe('When no reference provided, SnameForm', () => {
	let store
	beforeEach(() => {
		store = mockStore({
			ref: refReducer([], { type: 'INIT', ref: {} }),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
			names: nameReducer([], { type: 'INIT' }),
		})
		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<SnameForm
					displaySnameForm='block'
					showNewSnameForm={() => {}}
					newSnameButtonIsDisabled={true}
					setNewSnameButtonIsDisabled={() => {}}
					setFocusOnSnameButton={() => {}}
					displayRefForm='none'
					deleteCreatedSname={false}
					setDeleteCreatedSname={() => {}}
				/>
			</Provider>
		)
		utilities.findDuplicateStructuredNames.mockImplementation(
			(sname, structuredNames) => []
		)
	})
	test('does not allow to add new sname', async () => {
		const saveButton = screen.getByRole('button', { name: /save/i })
		userEvent.click(saveButton)
		const refNotProvidedError = await screen.findByText(
			/Enter reference before saving a structured name/i
		)
		expect(refNotProvidedError).toBeInTheDocument()
	})
})

test('does not add duplicate names', () => {
	const mapStateWithNameAdded = {
		...initialMapState,
		'{"type":"name","value":200}': {
			id: '{"type":"name","value":200}',
			name: 'newName',
			variant: 'name',
		},
	}

	const store = mockStore({
		ref: refReducer([], addRef(reference)),
		sname: snameReducer([], { type: 'INIT', sname: {} }),
		map: mapReducer(mapStateWithNameAdded, { type: 'INIT' }),
		names: nameReducer(
			[],
			addName({
				id: '{"type":"name","value":200}',
				name: 'newName',
				variant: 'name',
			})
		),
	})

	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<SnameForm
				displaySnameForm='block'
				showNewSnameForm={() => {}}
				newSnameButtonIsDisabled={true}
				setNewSnameButtonIsDisabled={() => {}}
				setFocusOnSnameButton={() => {}}
				displayRefForm='none'
				deleteCreatedSname={false}
				setDeleteCreatedSname={() => {}}
			/>
		</Provider>
	)
	utilities.findDuplicateStructuredNames.mockImplementation(
		(sname, structuredNames) => []
	)

	const saveButton = screen.getByRole('button', { name: /save/i })
	const inputFields = screen.getAllByRole('combobox')
	const nameInput = inputFields[0]
	const qualifierInput = inputFields[1]
	const locationInput = inputFields[2]
	const qualifierDropdown = screen.getByTestId('datalist-test-id-qualifier')
	const selectedQualifierOption = qualifierDropdown
		.querySelector('option[value="Bio_Brachiopoda"]')
		.getAttribute('value')
	const locationDropdown = screen.getByTestId('datalist-test-id-location')
	const selectedLocationOption = locationDropdown
		.querySelector('option[value="Alabama"]')
		.getAttribute('value')
	userEvent.type(nameInput, 'newName')
	userEvent.type(qualifierInput, selectedQualifierOption)
	userEvent.type(locationInput, selectedLocationOption)
	userEvent.click(saveButton)
	expect(store.dispatch).toHaveBeenCalledTimes(2)
	expect(store.dispatch).toHaveBeenNthCalledWith(1, {
		type: 'ADD',
		sname: {
			id: expect.anything(),
			name_id: '{"type":"name","value":200}',
			location_id: '{"type":"db_location","value":37}',
			qualifier_id: '{"type":"db_qualifier","value":36}',
			reference_id: -1,
			remarks: '',
			save_with_reference_id: false,
		},
	})
})

test('does not add duplicate locations', () => {
	const mapStateWithNameAdded = {
		...initialMapState,
		'{"type":"location","value":201}': {
			id: '{"type":"location","value":201}',
			name: 'newLocation',
			variant: 'location',
		},
	}

	const store = mockStore({
		ref: refReducer([], addRef(reference)),
		sname: snameReducer([], { type: 'INIT', sname: {} }),
		map: mapReducer(mapStateWithNameAdded, { type: 'INIT' }),
		names: nameReducer(
			[],
			addName({
				id: '{"type":"location","value":201}',
				name: 'newLocation',
				variant: 'location',
			})
		),
	})

	store.dispatch = jest.fn()
	render(
		<Provider store={store}>
			<SnameForm
				displaySnameForm='block'
				showNewSnameForm={() => {}}
				newSnameButtonIsDisabled={true}
				setNewSnameButtonIsDisabled={() => {}}
				setFocusOnSnameButton={() => {}}
				displayRefForm='none'
				deleteCreatedSname={false}
				setDeleteCreatedSname={() => {}}
			/>
		</Provider>
	)
	utilities.findDuplicateStructuredNames.mockImplementation(
		(sname, structuredNames) => []
	)

	const saveButton = screen.getByRole('button', { name: /save/i })
	const inputFields = screen.getAllByRole('combobox')
	const nameInput = inputFields[0]
	const qualifierInput = inputFields[1]
	const locationInput = inputFields[2]
	const nameDropdown = screen.getByTestId('datalist-test-id-name')
	const selectedNameOption = nameDropdown
		.querySelector('option[value="1b"]')
		.getAttribute('value')
	const qualifierDropdown = screen.getByTestId('datalist-test-id-qualifier')
	const selectedQualifierOption = qualifierDropdown
		.querySelector('option[value="Bio_Brachiopoda"]')
		.getAttribute('value')
	userEvent.type(nameInput, selectedNameOption)
	userEvent.type(qualifierInput, selectedQualifierOption)
	userEvent.type(locationInput, 'newLocation')
	userEvent.click(saveButton)
	expect(store.dispatch).toHaveBeenCalledTimes(2)
	expect(store.dispatch).toHaveBeenNthCalledWith(1, {
		type: 'ADD',
		sname: {
			id: expect.anything(),
			name_id: '{"type":"db_name","value":241}',
			location_id: '{"type":"location","value":201}',
			qualifier_id: '{"type":"db_qualifier","value":36}',
			reference_id: -1,
			remarks: '',
			save_with_reference_id: false,
		},
	})
})

describe('When user tries to create duplicate structured name', () => {
	test('prevents submission and shows notification', async () => {
		const store = mockStore({
			ref: refReducer([], addRef(reference)),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
			names: nameReducer([], { type: 'INIT' }),
		})

		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<SnameForm
					displaySnameForm='block'
					showNewSnameForm={() => {}}
					newSnameButtonIsDisabled={true}
					setNewSnameButtonIsDisabled={() => {}}
					setFocusOnSnameButton={() => {}}
					displayRefForm='none'
					deleteCreatedSname={false}
					setDeleteCreatedSname={() => {}}
				/>
			</Provider>
		)
		utilities.findDuplicateStructuredNames.mockImplementation(
			(sname, structuredNames) => [
				{
					id: '{"type":"structured_name","value":100}',
					name_id: '{"type":"db_name","value":241}',
					location_id: '{"type":"db_location","value":37}',
					qualifier_id: '{"type":"db_qualifier","value":36}',
					reference_id: -1,
					remarks: '',
					save_with_reference_id: false,
				},
			]
		)
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveButton)
		const duplicateSnameError = await screen.findByText(
			/You are attempting to create a duplicate structured name/i
		)
		expect(store.dispatch).not.toHaveBeenCalled()
		expect(duplicateSnameError).toBeInTheDocument()
	})

	test('allows user to select option for making duplicate sname', async () => {
		const store = mockStore({
			ref: refReducer([], addRef(reference)),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
			names: nameReducer([], { type: 'INIT' }),
		})

		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<SnameForm
					displaySnameForm='block'
					showNewSnameForm={() => {}}
					newSnameButtonIsDisabled={true}
					setNewSnameButtonIsDisabled={() => {}}
					setFocusOnSnameButton={() => {}}
					displayRefForm='none'
					deleteCreatedSname={false}
					setDeleteCreatedSname={() => {}}
				/>
			</Provider>
		)
		utilities.findDuplicateStructuredNames.mockImplementation(
			(sname, structuredNames) => [
				{
					id: '{"type":"structured_name","value":100}',
					name_id: '{"type":"db_name","value":241}',
					location_id: '{"type":"db_location","value":37}',
					qualifier_id: '{"type":"db_qualifier","value":36}',
					reference_id: -1,
					remarks: '',
					save_with_reference_id: false,
				},
			]
		)
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveButton)
		const okButton = await screen.findByText(/ok/i)
		userEvent.click(okButton)
		expect(store.dispatch).toHaveBeenCalledTimes(2)
		expect(store.dispatch).toHaveBeenNthCalledWith(1, {
			type: 'ADD',
			sname: {
				id: expect.anything(),
				name_id: '{"type":"db_name","value":241}',
				location_id: '{"type":"db_location","value":37}',
				qualifier_id: '{"type":"db_qualifier","value":36}',
				reference_id: -1,
				remarks: '',
				save_with_reference_id: true,
			},
		})
	})

	test('allows to choose existing structured name instead of creating a new one', async () => {
		const store = mockStore({
			ref: refReducer([], addRef(reference)),
			sname: snameReducer([], { type: 'INIT', sname: {} }),
			map: mapReducer(initialMapState, { type: 'INIT' }),
			names: nameReducer([], { type: 'INIT' }),
		})

		store.dispatch = jest.fn()
		render(
			<Provider store={store}>
				<SnameForm
					displaySnameForm='block'
					showNewSnameForm={() => {}}
					newSnameButtonIsDisabled={true}
					setNewSnameButtonIsDisabled={() => {}}
					setFocusOnSnameButton={() => {}}
					displayRefForm='none'
					deleteCreatedSname={false}
					setDeleteCreatedSname={() => {}}
				/>
			</Provider>
		)
		utilities.findDuplicateStructuredNames.mockImplementation(
			(sname, structuredNames) => [
				{
					id: '{"type":"structured_name","value":100}',
					name_id: '{"type":"db_name","value":241}',
					location_id: '{"type":"db_location","value":37}',
					qualifier_id: '{"type":"db_qualifier","value":36}',
					reference_id: -1,
					remarks: '',
					save_with_reference_id: false,
				},
			]
		)
		const saveButton = screen.getByRole('button', { name: /save/i })
		const inputFields = screen.getAllByRole('combobox')
		const nameInput = inputFields[0]
		const qualifierInput = inputFields[1]
		const locationInput = inputFields[2]
		const nameDropdown = screen.getByTestId('datalist-test-id-name')
		const selectedNameOption = nameDropdown
			.querySelector('option[value="1b"]')
			.getAttribute('value')
		const qualifierDropdown = screen.getByTestId(
			'datalist-test-id-qualifier'
		)
		const selectedQualifierOption = qualifierDropdown
			.querySelector('option[value="Bio_Brachiopoda"]')
			.getAttribute('value')
		const locationDropdown = screen.getByTestId('datalist-test-id-location')
		const selectedLocationOption = locationDropdown
			.querySelector('option[value="Alabama"]')
			.getAttribute('value')
		userEvent.type(nameInput, selectedNameOption)
		userEvent.type(qualifierInput, selectedQualifierOption)
		userEvent.type(locationInput, selectedLocationOption)
		userEvent.click(saveButton)
		const selectExistingSnameButton = await screen.findAllByRole('button', {
			name: /select/i,
		})
		userEvent.click(selectExistingSnameButton[0])
		const okButton = screen.getByText(/ok/i)
		userEvent.click(okButton)
		expect(store.dispatch).toHaveBeenCalledTimes(1)
		expect(store.dispatch).toHaveBeenCalledWith({
			type: 'SELECT_STRUCTURED_NAME',
			structured_name_id: '{"type":"structured_name","value":100}',
		})
	})
})
