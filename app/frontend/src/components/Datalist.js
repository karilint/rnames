import React from 'react'

export const Datalist = ({ name, options, value, onChange, innerRef }) => {
	return (
		<>
			<input
				className='w3-input w3-border w3-border-dark-grey'
				type='text'
				list={name}
				value={value}
				onChange={onChange}
				ref={innerRef}
			/>
			<datalist id={name} data-testid={`datalist-test-id-${name}`}>
				{options.map(tuple => (
					<option key={tuple[0]} value={tuple[1]} />
				))}
			</datalist>
		</>
	)
}
