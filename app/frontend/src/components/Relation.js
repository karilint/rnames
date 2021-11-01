import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { loadServerData } from '../services/server'
import { updateRel, deleteRel } from '../store/relations/actions'
import { SnameOption } from './SnameOption'
import { formatStructuredName } from '../utilities'

export const Relation = ({ data }) => {
	const dispatch = useDispatch()
	const [snames, name1text, name2text] = useSelector(v => {
		const sname1 = v.map[data.name1]
		const sname2 = v.map[data.name2]
		return [
			v.sname.concat(loadServerData('structured_names')).map(v => v.id),
			sname1 ? formatStructuredName(sname1, v) : '',
			sname2 ? formatStructuredName(sname2, v) : '',
		]
	})

	const [name1, setName1Text] = useState(name1text)
	const [name2, setName2Text] = useState(name2text)

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
				value={name1}
				onChange={e => {
					update(e, 'name1')
					setName1Text(e.target.value)
				}}
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
				value={name2}
				onChange={e => {
					update(e, 'name2')
					setName2Text(e.target.value)
				}}
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
