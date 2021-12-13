import React from 'react'
import { useSelector } from 'react-redux'

export const SnameTooltip = ({ sname }) => {
	console.log(sname)
	const qualifierName = {
		1: 'Chronostratigraphy',
		2: 'Lithostratigraphy',
		3: 'Regional Standard',
		4: 'Chemostratigraphy',
		5: 'Biostratigraphy',
		6: 'Sequence-stratigraphy',
	}

	const data = useSelector(state => {
		return {
			...sname,
			reference: state.map[sname.reference_id],
			name: state.map[sname.name_id],
			qualifier: state.map[sname.qualifier_id],
			qualifierName:
				state.map[state.map[sname.qualifier_id].qualifier_name_id],
			location: state.map[sname.location_id],
		}
	})

	const remarks = data.remarks ? <p>Remarks: {data.remarks}</p> : <></>
	const reference = data.reference ? (
		<p>{`${data.reference.title} (${data.reference.year})`}</p>
	) : (
		<></>
	)

	return (
		<div className='tooltip-wrapper'>
			<div className='w3-card w3-white w3-container w3-padding-16 tooltip-content'>
				<p>{data.name.name}</p>
				<p>{data.location.name}</p>
				<p>{data.qualifierName.name}</p>
				<p>
					{`${
						qualifierName[data.qualifier.stratigraphic_qualifier_id]
					} level ${1}`}
				</p>
				{remarks}
				{reference}
			</div>
		</div>
	)
}
