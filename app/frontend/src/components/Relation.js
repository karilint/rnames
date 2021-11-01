import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { loadServerData } from '../services/server'
import { updateRel, deleteRel } from '../store/relations/actions'
import { SnameOption } from './SnameOption'

export const Relation = ({ data }) => {
	const dispatch = useDispatch()
	const snames = useSelector(v =>
		v.sname.concat(loadServerData('structured_names')).map(v => v.id)
	)

	const update = ({ target }, field) => {
		const r = { ...data }
		r[field] = target.value
		dispatch(updateRel(r))
	}

	const deleteRelHandler = () => {
		dispatch(deleteRel(data))
	}

	const id1 = `${data.id}-name1`
	const id2 = `${data.id}-name2`

	return (
		<div>
			<label htmlFor='name1'>Name 1</label>
			<input
				name='name1'
				type='text'
				value={data.name1 == -1 ? '' : data.name1}
				onChange={e => update(e, 'name1')}
				list={id1}
			/>
			<datalist id={id1}>
				{snames.map(v => (
					<SnameOption key={v} data={v} />
				))}
			</datalist>
			<br />
			<label htmlFor='name2'>Name 2</label>
			<input
				name='name2'
				type='text'
				value={data.name2 == -1 ? '' : data.name2}
				onChange={e => update(e, 'name2')}
				list={id2}
			/>
			<datalist id={id2}>
				{snames.map(v => (
					<SnameOption key={v} data={v} />
				))}
			</datalist>
			<br />
			<button type='button' onClick={deleteRelHandler}>
				Delete
			</button>
		</div>
	)
}
