import React from 'react'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { loadServerData, initServer } from './services/server'
import { makeId } from './utilities'
import { initMapvalues } from './store/map/actions'
import { addRel } from './store/relations/actions'
import { addSname } from './store/snames/actions'
import { Reference } from './components/Reference'
import { Sname } from './components/Sname'
import { Relation } from './components/Relation'
import { Submit } from './components/Submit'
import { ReferenceForm } from './components/ReferenceForm'
import { SnameForm } from './components/SnameForm'

const blankRel = () => {
	return { id: makeId('relation'), name1: -1, name2: -1, reference_id: -1 }
}

const App = () => {
	const state = useSelector(v => v)
	const dispatch = useDispatch()

	const [displayRefForm, setDisplayRefForm] = useState('block')
	const [displaySnameForm, setDisplaySnameForm] = useState('none')
	const [newSnameButtonIsDisabled, setNewSnameButtonIsDisabled] =
		useState(false)

	useEffect(() => {
		initServer()
		const serverData = loadServerData()
		const map = {}
		serverData.names.forEach(v => (map[v.id] = v))
		serverData.locations.forEach(v => (map[v.id] = v))
		serverData.qualifier_names.forEach(v => (map[v.id] = v))
		serverData.qualifiers.forEach(v => (map[v.id] = v))
		serverData.structured_names.forEach(v => (map[v.id] = v))
		serverData.references.forEach(v => (map[v.id] = v))
		dispatch(initMapvalues(map))
	}, [])

	const addRelHandler = e => {
		dispatch(addRel(blankRel()))
	}

	const showNewReferenceForm = () => {
		setDisplayRefForm(displayRefForm === 'none' ? 'block' : 'none')
	}

	const showNewSnameForm = () => {
		setDisplaySnameForm(displaySnameForm === 'none' ? 'block' : 'none')
		setNewSnameButtonIsDisabled(!newSnameButtonIsDisabled)
	}

	return (
		<>
			<div>
				<h2>References</h2>
				{state.ref.length === 0 ? (
					<ReferenceForm
						{...{
							displayRefForm,
							showNewReferenceForm,
						}}
					/>
				) : (
					state.ref.map(reference =>
						reference.edit ? (
							<ReferenceForm
								key={reference.id}
								reference={reference}
								displayRefForm={displayRefForm}
								showNewReferenceForm={showNewReferenceForm}
								isQueried={true}
							/>
						) : (
							<Reference
								{...{
									key: reference.id,
									reference,
									showNewReferenceForm,
								}}
							/>
						)
					)
				)}
			</div>
			<div>
				<h2>Structured Names</h2>
				{state.sname.map(sname => (
					<Sname {...{ key: sname.id, sname }} />
				))}
				<SnameForm
					{...{
						displaySnameForm,
						showNewSnameForm,
						newSnameButtonIsDisabled,
						setNewSnameButtonIsDisabled,
					}}
				/>
				<button
					type='button'
					onClick={showNewSnameForm}
					disabled={newSnameButtonIsDisabled}
				>
					Add new structured name
				</button>
			</div>
			<div>
				<h2>Relations</h2>
				{state.rel.map(data => (
					<Relation {...{ key: data.id, data }} />
				))}
				<button type='button' onClick={addRelHandler}>
					Add new relation
				</button>
			</div>
			<Submit />
		</>
	)
}

export default App
