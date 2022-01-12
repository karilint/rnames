import React from 'react'
import { Notification } from './Notification'

export const HorizontalInputField = ({
	label,
	name,
	value,
	notification,
	setField,
	autoFocus,
}) => {
	return (
		<>
			<div className='w3-row v-center'>
				<div className='w3-quarter'>
					<label htmlFor={name}>
						<p>
							<b>{label || name}</b>
						</p>
					</label>
				</div>
				<div className='w3-rest flex-grow'>
					<input
						className='w3-input w3-border w3-border-dark-grey w3-rest'
						type='text'
						name={name}
						value={value}
						onChange={e => setField(e.target.value)}
						autoFocus={autoFocus}
					/>
				</div>

			</div>
			<Notification notification={notification} />
		</>
	)
}

export const InputField = ({
	label,
	name,
	value,
	notification,
	setField,
	autoFocus,
}) => {
	return (
		<div className='w3-row'>
			<label htmlFor={name}>
				<b>{label || name}</b>
			</label>
			<input
				className='w3-input w3-border w3-border-dark-grey'
				type='text'
				name={name}
				value={value}
				onChange={e => setField(e.target.value)}
				autoFocus={autoFocus}
			/>
			<Notification notification={notification} />
		</div>
	)
}
