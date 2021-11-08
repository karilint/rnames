import React from 'react'

export const Datalist = ({ name, options, value, onChange }) => {
	return (
		<>
			<input type='text' list={name} value={value} onChange={onChange} />
			<datalist id={name}>
				{options.map(tuple => (
					<option key={tuple[0]} value={tuple[1]} />
				))}
			</datalist>
		</>
	)
}
