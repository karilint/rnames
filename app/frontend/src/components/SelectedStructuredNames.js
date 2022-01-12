import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
	selectStructuredName,
	deselectStructuredName,
} from '../store/selected_structured_names/actions'
import { loadServerData } from '../services/server'
import { formatStructuredName, parseId } from '../utilities'

export const SelectedStructuredNames = () => {
	const [selection, dbNames] = useSelector(state => {
		const formatName = sname => {
			const hasReference = state.map[sname.reference_id] !== undefined

			return `${formatStructuredName(sname, state)} (${
				hasReference ? `${state.map[sname.reference_id].title}, ` : ''
			}${parseId(sname.id).value})`
		}

		return [
			state.selectedStructuredNames
				.filter(v => parseId(v).type !== 'structured_name')
				.map(v => {
					return {
						id: v,
						formattedName: formatName(state.map[v]),
					}
				}),
			(loadServerData('structured_names') || []).map(v => {
				return {
					...v,
					formattedName: formatName(v),
				}
			}),
		]
	})
	const relations = useSelector(v => v.rel)
	const [search, setSearch] = useState('')
	const dispatch = useDispatch()
	const dataListId = 'selectedStructuredNamesDataList'

	const handleChange = e => {
		const result = dbNames.find(v => e.target.value === v.formattedName)
		if (result) {
			setSearch('')
			dispatch(selectStructuredName(result.id))
		} else {
			setSearch(e.target.value)
		}
	}

	const handleDelete = id => {
		if (!relations.find(v => v.name1 === id || v.name2 === id))
			dispatch(deselectStructuredName(id))
		document.getElementById('select-existing-name').focus()
	}

	return (
		<>
			<label>
				<b>Select existing name</b>
			</label>
			<input
				className='w3-input w3-border w3-border-dark-grey'
				type='text'
				list={dataListId}
				value={search}
				onChange={handleChange}
				id='select-existing-name'
			/>
			<datalist id={dataListId}>
				{dbNames.map(v => (
					<option key={v.id}>{v.formattedName}</option>
				))}
			</datalist>
			{selection.map(v => (
				<div key={v.id}>
					<p>
						{v.formattedName}
						<button
							className='w3-button w3-grey w3-circle w3-margin-left'
							type='button'
							onClick={() => handleDelete(v.id)}
						>
							<i title='Deselect' className='fa fa-trash'></i>
						</button>
					</p>
				</div>
			))}
		</>
	)
}
