import React from 'react'
import { useSelector } from 'react-redux'
import { formatStructuredName } from '../utilities'

export const SnameOption = ({ data }) => {
	const text = useSelector(v => formatStructuredName(v.map[data], v))
	return <option key={data} value={data}>{text}</option>
}
