import React, { useState } from 'react'
import { useSelector } from 'react-redux'
import { formatStructuredName } from '../utilities'
import { selectMap } from '../store/snames/selectors'

const infoMsg =
	'You are attempting to create a duplicate structured name. \
	Please select an existing name to use or confirm that you wish to create a new name.'

export const DuplicateNameDialog = ({
	structuredName,
	duplicateNames,
	selectHandler,
	cancelHandler,
}) => {
	const [id, setId] = useState(structuredName.id)
	const [saveWithReference, setSaveWithReference] = useState(true)
	const [remarks, setRemarks] = useState('')
	const map = useSelector(selectMap)

	const doiUrl = refId => `https://www.doi.org/${map[refId].doi}`

	const submit = () => {
		if (id === structuredName.id) {
			const name = {
				...structuredName,
				remarks,
				save_with_reference_id: saveWithReference,
			}

			selectHandler(name)
		} else {
			selectHandler(duplicateNames.find(v => v.id === id))
		}
	}

	const checkboxId = 'duplicate-name-dialog-save-with-reference'

	return (
		<div className='w3-card w3-container w3-padding-16 w3-white'>
			<p>{infoMsg}</p>
			<div>
				<button
					className={`w3-button ${
						id === structuredName.id ? 'w3-grey' : ''
					}`}
					onClick={() => setId(structuredName.id)}
				>
					{`Create a new name "${formatStructuredName(
						structuredName,
						{ map }
					)}"`}
				</button>
				<p>
					<input
						type='checkbox'
						className='w3-check'
						id={checkboxId}
						checked={saveWithReference}
						onChange={() =>
							setSaveWithReference(!saveWithReference)
						}
					/>
					<label htmlFor={checkboxId}>Save with reference id</label>
				</p>
				<input
					type='text'
					className='w3-input w3-border w3-border-dark-grey'
					value={remarks}
					onChange={e => setRemarks(e.target.value)}
					placeholder='Remarks...'
				/>
			</div>
			<p>Or select an existing name instead</p>
			{duplicateNames.map(v => (
				<div key={v.id}>
					<button
						className={`w3-button ${id === v.id ? 'w3-grey' : ''}`}
						onClick={() => setId(v.id)}
					>
						{`Select "${formatStructuredName(v, { map })}"`}
					</button>
					{map[v.reference_id] ? (
						<span>
							{'from '}
							<a
								target='_blank'
								rel='noreferrer'
								href={doiUrl(v.reference_id)}
							>
								{map[v.reference_id].title}
							</a>
						</span>
					) : (
						<></>
					)}
				</div>
			))}

			<div className='w3-bar w3-margin-top'>
				<div className='w3-quarter'>
					<button
						className={`w3-button w3-grey ${
							id !== undefined ? '' : 'w3-disabled'
						}`}
						onClick={() => submit()}
					>
						Ok
					</button>
				</div>
				<div className='w3-rest'>
					<button
						className={'w3-button w3-grey'}
						onClick={() => cancelHandler()}
					>
						Cancel
					</button>
				</div>
			</div>
		</div>
	)
}
