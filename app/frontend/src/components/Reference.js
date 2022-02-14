import React from 'react'
import { useDispatch } from 'react-redux'
import { updateRef } from '../store/references/actions'
import { ReferenceDisplay } from './ReferenceDisplay'

export const Reference = ({ reference, showNewReferenceForm }) => {
	const dispatch = useDispatch()

	return (
		<ReferenceDisplay reference={reference}>
			<button
				className='w3-button w3-grey'
				onClick={() => {
					dispatch(updateRef({ ...reference, edit: true }))
					showNewReferenceForm()
				}}
			>
				Edit
			</button>
		</ReferenceDisplay>
	)
}
