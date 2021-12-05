import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { InputField } from './InputField'
import { doiFormIsValid } from '../validations'
import { findDuplicateDois, findDuplicateLinks } from '../utilities'

export const DoiForm = ({
	doi,
	setQueried,
	setFirstAuthor,
	setYear,
	setTitle,
	setDoi,
	setLink,
	displayRefForm,
}) => {
	const [notification, setNotification] = useState(null)
	const notify = (message, type = 'error') => {
		setNotification({ message, type })
	}

	useEffect(() => {
		if (!notification) return

		const doiFormTimeoutId = setTimeout(() => {
			setNotification(null)
		}, 7000)
		return () => {
			clearTimeout(doiFormTimeoutId)
		}
	}, [notification])

	const doiSubmit = async e => {
		e.preventDefault()
		if (!doiFormIsValid(doi, notify)) return
		if (findDuplicateDois(doi)) {
			notify('An existing reference is using the same doi.')
			return
		}
		try {
			const result = await axios.get(
				`https://api.crossref.org/works/${doi}`
			)
			const response = JSON.parse(result.request.response).message

			if (response.author.length === 0) return

			setQueried(true)
			setFirstAuthor(
				`${response.author[0].given} ${response.author[0].family}`
			)
			setYear(response.created['date-parts'][0][0])
			setTitle(response.title[0])
			setDoi(response.DOI)
			setLink(response.URL)
		} catch (err) {
			notify(`No resources found with ${doi}`)
		}
	}

	return (
		<form onSubmit={doiSubmit} style={{ display: displayRefForm }}>
			<InputField
				name='doi'
				value={doi}
				setField={setDoi}
				notification={notification}
				autoFocus={true}
			/>
			<button type='submit'>get</button>
			<button type='button' onClick={() => setQueried(true)}>
				Manual Entry
			</button>
		</form>
	)
}
