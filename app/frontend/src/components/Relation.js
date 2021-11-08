import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { loadServerData } from '../services/server'
import { formatStructuredName } from '../utilities'
import { updateRel, deleteRel } from '../store/relations/actions'
import { Dropdown } from './Dropdown'

export const Relation = ({ data }) => {
	const dispatch = useDispatch()
	const state = useSelector(v => v)

	const name1Options = state.sname
		.concat(...loadServerData('structured_names'))
		.filter(v => v.id !== data.name2)
		.map(v => [v.id, formatStructuredName(v, state)])

	const name2Options = state.sname
		.concat(...loadServerData('structured_names'))
		.filter(v => v.id !== data.name1)
		.map(v => [v.id, formatStructuredName(v, state)])

	const update = ({ target }, field) => {
		const r = { ...data }
		r[field] = target.value
		dispatch(updateRel(r))
	}

	const refOptions = state.ref
		.concat(...loadServerData('references'))
		.map(v => [v.id, v.title])
	
	const deleteRelHandler = () => {
		dispatch(deleteRel(data))
	}

	return (
		<div>
			<label htmlFor='reference'>Reference</label>
			<Dropdown
				name='reference'
				options={refOptions}
				value={data.reference_id}
				onChange={e => update(e, 'reference_id')}
			/>
			<br />
			<Dropdown
				options={name1Options}
				value={data.name1}
				onChange={e => update(e, 'name1')}
			/>
			<br />
			<Dropdown
				options={name2Options}
				value={data.name2}
				onChange={e => update(e, 'name2')}
			/>
			<br />
			<button type='button' onClick={deleteRelHandler}>
				Delete
			</button>
		</div>
	)
}
