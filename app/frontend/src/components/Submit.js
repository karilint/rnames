import React from 'react'
import { useSelector } from 'react-redux'
import axios from 'axios'

export const Submit = () => {
	const data = useSelector(v => {
		return {
			reference: v.ref[0],
			structured_names: v.sname,
			relations: v.rel,
			names: v.names,
		}
	})

	const submit = async () => {
		const parseIds = (obj, keys = []) => {
			const ret = { ...obj }
			keys.forEach(k => (ret[k] = JSON.parse(ret[k])))
			return ret
		}

		const submit_data = {
			names: data.names.map(v => parseIds(v, ['id'])),
			reference: parseIds(data.reference, ['id']),
			relations: data.relations.map(v =>
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

		console.log(submit_data)

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
			.then(res => document.body.innerHTML = res.data)
			.catch(err => console.log(err))
	}

	return <button onClick={e => submit()}>Submit</button>
}
