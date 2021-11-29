import React from 'react'
import { expect, test, beforeEach, describe, jest } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import { DoiForm } from '../DoiForm'
import { foundDoiResponseData } from '../test/data/crossapiResponse'
import * as utilities from '../../utilities.js'

jest.mock('axios')
jest.mock('../../utilities.js')

const doi = '10.1002/spp2.1267'
const setQueried = () => {}
const setFirstAuthor = () => {}
const setYear = () => {}
const setTitle = () => {}
const setDoi = () => {}
const setLink = () => {}

describe('When reference form set to visible', () => {
	beforeEach(() => {
		render(
			<DoiForm
				{...{
					doi,
					setQueried,
					setFirstAuthor,
					setYear,
					setTitle,
					setDoi,
					setLink,
				}}
				displayRefForm='block'
			/>
		)
	})
	test('rendered doi form has two buttons', () => {
		expect(screen.getAllByRole('button')).toHaveLength(2)
	})

	test('rendered doi form has input field', () => {
		expect(screen.getByRole('textbox')).toBeInTheDocument()
	})

	test('error msg does not get printed on succefful response from crossrefapi', async () => {
		const data = {
			request: { response: JSON.stringify(foundDoiResponseData) },
		}
		axios.get.mockImplementationOnce(() => Promise.resolve(data))
		utilities.findDuplicateDois.mockImplementationOnce(doi => [])
		utilities.findDuplicateLinks.mockImplementationOnce(doi => [])
		const getButton = screen.getAllByRole('button')[0]
		userEvent.click(getButton)
		const notification = await screen.queryByText(/no resources found/i)
		expect(notification).not.toBeInTheDocument()
	})

	test('error msg gets printed on unsuccefful response from crossrefapi', async () => {
		const data = { request: { response: 'Resource not found' } }
		axios.get.mockImplementationOnce(() => Promise.resolve(data))
		utilities.findDuplicateDois.mockImplementationOnce(doi => [])
		utilities.findDuplicateLinks.mockImplementationOnce(doi => [])
		const getButton = screen.getAllByRole('button')[0]
		userEvent.click(getButton)
		await screen.findByText(/no resources found/i)
	})

	test('error msg does not get printed if no doi or link duplicates found', async () => {
		const data = {
			request: { response: JSON.stringify(foundDoiResponseData) },
		}
		axios.get.mockImplementationOnce(() => Promise.resolve(data))
		utilities.findDuplicateDois.mockImplementationOnce(doi => [])
		utilities.findDuplicateLinks.mockImplementationOnce(doi => [])
		const getButton = screen.getAllByRole('button')[0]
		userEvent.click(getButton)
		const notification = await screen.queryByText(
			'An existing reference is using the same doi.'
		)
		expect(notification).not.toBeInTheDocument()
	})

	test('error msg gets printed if link duplicates found', async () => {
		const data = {
			request: { response: JSON.stringify(foundDoiResponseData) },
		}
		axios.get.mockImplementationOnce(() => Promise.resolve(data))
		utilities.findDuplicateDois.mockImplementationOnce(doi => [])
		utilities.findDuplicateLinks.mockImplementationOnce(doi => [
			{
				title: 'Katian (Ordovician) to Aeronian (Silurian, Llandovery) graptolite biostratigraphy of the YD-1 drill core, Yuanan County, Hubei Province, China',
				link: 'http://dx.doi.org/10.1002/spp2.1267',
			},
		])
		const getButton = screen.getAllByRole('button')[0]
		userEvent.click(getButton)
		const notification = await screen.queryByText(
			'An existing reference is using the same doi.'
		)
		expect(notification).toBeInTheDocument()
	})

	test('error msg gets printed if doi duplicates found', async () => {
		const data = {
			request: { response: JSON.stringify(foundDoiResponseData) },
		}
		axios.get.mockImplementationOnce(() => Promise.resolve(data))
		utilities.findDuplicateDois.mockImplementationOnce(doi => [
			{
				title: 'Katian (Ordovician) to Aeronian (Silurian, Llandovery) graptolite biostratigraphy of the YD-1 drill core, Yuanan County, Hubei Province, China',
				doi: '10.1002/spp2.1267',
			},
		])
		utilities.findDuplicateLinks.mockImplementationOnce(doi => [])
		const getButton = screen.getAllByRole('button')[0]
		userEvent.click(getButton)
		const notification = await screen.queryByText(
			'An existing reference is using the same doi.'
		)
		expect(notification).toBeInTheDocument()
	})
})

describe('When reference form set to invisible', () => {
	beforeEach(() => {
		render(
			<DoiForm
				{...{
					doi,
					setQueried,
					setFirstAuthor,
					setYear,
					setTitle,
					setDoi,
					setLink,
				}}
				displayRefForm='none'
			/>
		)
	})

	test('doi input field not visible', () => {
		expect(screen.queryByRole('textbox')).toBeNull()
	})
})

test('shows correct error msg on invalid doi and returns', async () => {
	render(
		<DoiForm
			{...{
				setQueried,
				setFirstAuthor,
				setYear,
				setTitle,
				setDoi,
				setLink,
			}}
			doi=''
			displayRefForm='block'
		/>
	)
	const data = { request: { response: 'Resource not found' } }
	axios.get.mockImplementationOnce(() => Promise.resolve(data))
	const getButton = screen.getAllByRole('button')[0]
	userEvent.click(getButton)
	const doiNotProvidedError = screen.getByText(
		'Please provide the doi number'
	)
	expect(doiNotProvidedError).toBeInTheDocument()
	const wrongDoiError = screen.queryByText(/No resources found/i)
	expect(wrongDoiError).not.toBeInTheDocument()
})
