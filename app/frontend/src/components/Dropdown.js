import React from 'react'

export const Dropdown = ({ name, options, value, onChange }) => {
	return (
		<select name={name} onChange={onChange} value={value}>
			<option></option>
			{options.map(tuple => (
				<option key={tuple[0]} value={tuple[0]}>
					{tuple[1]}
				</option>
			))}
		</select>
	)
}
