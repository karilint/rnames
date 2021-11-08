import React from 'react'
import { useDispatch } from 'react-redux'
import { updateRef } from '../store/references/actions'

export const Reference = ({ reference, showNewReferenceForm }) => {
	const dispatch = useDispatch()

	return (
		<div>
			<p>first_author: {reference.firstAuthor}</p>
			<p>year: {reference.year}</p>
			<p>title: {reference.title}</p>
			<p>doi: {reference.doi}</p>
			<p>link: {reference.link}</p>
			<button
				type='button'
				onClick={() => {
					dispatch(updateRef({ ...reference, edit: true }))
					showNewReferenceForm()
				}}
			>
				edit
			</button>
		</div>
	)
}
