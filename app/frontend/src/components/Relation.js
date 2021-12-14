import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { formatStructuredName } from '../utilities'
import { updateRel } from '../store/relations/actions'

export const Relation = ({ relation }) => {
	const dispatch = useDispatch()
	const [formattedName1, formattedName2] = useSelector(state => {
		return [
			formatStructuredName(state.map[relation.name1], state),
			formatStructuredName(state.map[relation.name2], state),
		]
	})

	const swap = () => {
		dispatch(
			updateRel({
				...relation,
				name1: relation.name2,
				name2: relation.name1,
			})
		)
	}

	const belongs = () => {
		dispatch(
			updateRel({
				...relation,
				belongs_to: relation.belongs_to === 1 ? 0 : 1,
			})
		)
	}

	return (
		<div className='w3-row v-center'>
			<div className='w3-col s5 w3-center hide-overflow'>
				<p>{formattedName1}</p>
			</div>
			<div className='w3-col s1 w3-center'>
				<button className='w3-button' onClick={swap}>
					↔
				</button>
			</div>
			<div className='w3-col s1 w3-center'>
				<input
					className='w3-check check-notop'
					type='checkbox'
					onChange={belongs}
					checked={relation.belongs_to}
				/>
			</div>
			<div className='w3-col s5 w3-center hide-overflow'>
				<p>{formattedName2}</p>
			</div>
		</div>
	)
}
