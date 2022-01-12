import React from 'react'
import { useDispatch } from 'react-redux'
import { addRel, updateRel } from '../store/relations/actions'
import { makeId } from '../utilities'

export const BelongsToSelector = ({ idA, idB, relation = undefined }) => {
	const dispatch = useDispatch()

	const update = (name1, name2, belongs_to) => {
		if (relation) {
			dispatch(
				updateRel({
					...relation,
					name1,
					name2,
					belongs_to,
				})
			)
		} else {
			dispatch(
				addRel({
					id: makeId('relation'),
					name1,
					name2,
					belongs_to,
					reference_id: -1,
				})
			)
		}
	}

	const rightToLeft = e => {
		e.stopPropagation()
		update(idA, idB, 1)
	}

	const leftToRight = e => {
		e.stopPropagation()
		update(idB, idA, 1)
	}

	const noInclusion = e => {
		e.stopPropagation()
		update(
			relation ? relation.name1 : idA,
			relation ? relation.name2 : idB,
			0
		)
	}

	const belongsTo = relation ? relation.belongs_to : false

	return (
		<>
			<div
				className={`w3-button w3-bar-item ${
					belongsTo && relation.name1 === idA ? 'w3-grey' : ''
				}`}
				data-testid='rightToLeft-test-id'
				onClick={rightToLeft}
			>
				←
			</div>
			<div
				className={`w3-button w3-bar-item ${
					relation && !belongsTo ? 'w3-grey' : ''
				}`}
				data-testid='noInclusion-test-id'
				onClick={noInclusion}
			>
				↔
			</div>
			<div
				className={`w3-button w3-bar-item ${
					belongsTo && relation.name1 === idB ? 'w3-grey' : ''
				}`}
				data-testid='leftToRight-test-id'
				onClick={leftToRight}
			>
				→
			</div>
		</>
	)
}
