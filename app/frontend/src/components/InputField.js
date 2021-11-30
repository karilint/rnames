import React from 'react'
import { Notification } from './Notification'

export const InputField = ({ name, value, notification, setField, autoFocus }) => {
	return (
		<>
			<label htmlFor={name}>{name}</label>
			<input
				type='text'
				name={name}
				value={value}
				onChange={e => setField(e.target.value)}
				autoFocus={autoFocus}
			/>
			<Notification notification={notification} />
			<br />
		</>
	)
}
