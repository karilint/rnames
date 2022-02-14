import React, { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import axios from 'axios'
import { updateRefForSubmission } from '../validations'
import { Notification } from './Notification'
import { loadServerData } from '../services/server'
import { isDbId } from '../utilities'

export const Submit = () => {
	const data = useSelector(v => {
		return {
			reference: v.ref[0],
			structured_names: v.sname,
			relations: v.rel,
			names: v.names,
		}
	})
	const [notification, setNotification] = useState(null)

	useEffect(() => {
		if (!notification) return
		setTimeout(() => {
			setNotification(null)
		}, 7000)
	}, [notification])

	const notify = (message, type = 'error') => {
		setNotification({ message, type })
	}

	const submit = async () => {
		if (!data.reference) {
			notify('Please add reference before submitting')
			return
		}

		if (data.reference && data.reference.edit) {
			notify('Please save changes made in reference before submitting')
			return
		}

		if (data.relations.length === 0) {
			notify(
				'Please add structured names and relations before submitting'
			)
			return
		}

		const parseIds = (obj, keys = []) => {
			const ret = { ...obj }
			keys.forEach(k => (ret[k] = JSON.parse(ret[k])))
			return ret
		}

		const relationChanged = (relation) => {
			if (!isDbId(relation.id))
				return true

			const serverData = loadServerData()
			const compare = serverData.amendInfo.relations.find(v => v.id === relation.id)

			// If names are flipped but neither name belongs to the other
			// there is no need to update
			if (relation.belongs_to === compare.belongs_to
				&& relation.belongs_to === 0
				&& relation.name1 === compare.name2
				&& relation.name2 === compare.name1)
				return false

			return relation.name1 !== compare.name1
				|| relation.name2 !== compare.name2
				|| relation.belongs_to !== compare.belongs_to
		}

		const refWithNullValues = updateRefForSubmission(data.reference)

		const submit_data = {
			names: data.names.map(v => parseIds(v, ['id'])),
			reference: parseIds(refWithNullValues, ['id']),
			relations: data.relations.filter(v => relationChanged(v))
				.map(v =>
					parseIds(v, ['id', 'name1', 'name2'])
				),
			structured_names: data.structured_names.map(v =>
				parseIds(v, [
					'id',
					'location_id',
					'name_id',
					'qualifier_id',
					'reference_id',
				])
			),
		}

		const csrfmiddlewaretoken = document.querySelector(
			'[name=csrfmiddlewaretoken]'
		).value

		axios({
			url: '/wizard_submit',
			method: 'POST',
			headers: {
				'X-CSRFToken': csrfmiddlewaretoken,
			},
			data: submit_data,
		})
			// Django cleans fields when filling templates so this is safe
			.then(res => (document.body.innerHTML = res.data))
			.catch(err => console.log(err))
	}

	return (
		<>
			<Notification notification={notification} />
			<button type='button' className='w3-grey w3-button' onClick={e => submit()}>Submit</button>
		</>
	)
}
