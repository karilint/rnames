import React, { useState, useEffect } from 'react'
import { useDispatch } from 'react-redux'
import axios from 'axios'
import { addRef, deleteRef, updateRef } from '../store/references/actions'
import { makeId } from '../utilities'
import { Notification } from './Notification'

export const ReferenceForm = ({
	displayRefForm,
	showNewReferenceForm,
	reference = undefined,
	isQueried = false,
}) => {
	const dispatch = useDispatch()

	const [firstAuthor, setFirstAuthor] = useState('')
	const [year, setYear] = useState(0)
	const [title, setTitle] = useState('')
	const [doi, setDoi] = useState('')
	const [link, setLink] = useState('')
	const [exists, setExists] = useState(false)
	const [queried, setQueried] = useState(isQueried)
	const [notification, setNotification] = useState(null)

	useEffect(() => {
		if (!reference) return
		setFirstAuthor(reference.firstAuthor)
		setYear(reference.year)
		setTitle(reference.title)
		setDoi(reference.doi)
		setLink(reference.link)
		setExists(reference.exists)
	}, [])
  
  const notify = (message, type='error') => {
		setNotification({ message, type })
		setTimeout(() => {
		  setNotification(null)
		}, 7000)
	}

	const doiSubmit = async e => {
		e.preventDefault()

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

	const clearFields = () => {
		setFirstAuthor('')
		setYear(0)
		setTitle('')
		setDoi('')
		setLink('')
		setExists(false)
		setQueried(false)
	}

	const handleNewDoiSearch = () => {
		clearFields()
		dispatch(deleteRef(reference))
	}

	const handleManualSubmit = e => {
		e.preventDefault()
		const newReference = {
			firstAuthor,
			year,
			title,
			doi,
			link,
			exists,
			queried,
			edit: false,
		}

		if (!reference) {
			dispatch(addRef({ ...newReference, id: makeId('reference') }))
		} else {
			dispatch(updateRef({ ...newReference, id: reference.id }))
		}

		clearFields()
		showNewReferenceForm()
	}

	if (queried)
		return (
			<div>
				<form onSubmit={handleManualSubmit}>
					<label htmlFor='first_author'>first_author</label>
					<input
						type='text'
						name='first_author'
						value={firstAuthor}
						onChange={e => setFirstAuthor(e.target.value)}
					/>
					<br />
					<label htmlFor='year'>year</label>
					<input
						type='text'
						name='year'
						value={year}
						onChange={e => setYear(e.target.value)}
					/>
					<br />
					<label htmlFor='title'>title</label>
					<input
						type='text'
						name='title'
						value={title}
						onChange={e => setTitle(e.target.value)}
					/>
					<br />
					<label htmlFor='doi'>doi</label>
					<input
						type='text'
						name='doi'
						value={doi}
						onChange={e => setDoi(e.target.value)}
					/>
					<br />
					<label htmlFor='link'>link</label>
					<input
						type='text'
						name='link'
						value={link}
						onChange={e => setLink(e.target.value)}
					/>
					<br />
					<button type='submit'>Save reference</button>
					{reference ? (
						<>
							<br />
							<button type='button' onClick={handleNewDoiSearch}>
								Make new doi search
							</button>
						</>
					) : (
						''
					)}
				</form>
			</div>
		)

	return (
		<>
			<Notification notification={notification}/>
			<form onSubmit={doiSubmit} style={{ display: displayRefForm }}>
				<label htmlFor='doi'>doi</label>
				<input
					type='text'
					name='doi'
					value={doi}
					onChange={e => setDoi(e.target.value)}
				/>
				<button type='submit'>get</button>
				<button type='button' onClick={() => setQueried(true)}>
					Manual Entry
				</button>
			</form>
		</>
	)
}
