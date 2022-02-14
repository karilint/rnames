import React from 'react'
import { useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { loadServerData, initServer } from './services/server'
import { makeId, formatStructuredName } from './utilities'
import { initMapvalues } from './store/map/actions'
import { addRel } from './store/relations/actions'
import { addSname } from './store/snames/actions'
import { Reference } from './components/Reference'
import { ReferenceDisplay } from './components/ReferenceDisplay'
import { Sname } from './components/Sname'
import { Relation } from './components/Relation'
import { Submit } from './components/Submit'
import { ReferenceForm } from './components/ReferenceForm'
import { SnameForm } from './components/SnameForm'
import { SelectedStructuredNames } from './components/SelectedStructuredNames'
import { RelationSelector } from './components/RelationSelector'
import { Notification } from './components/Notification'
import { addRef } from './store/references/actions'
import { selectStructuredName } from './store/selected_structured_names/actions'

const App = () => {
	const state = useSelector(v => v)
	const dispatch = useDispatch()

	const [displayRefForm, setDisplayRefForm] = useState('block')
	const [displaySnameForm, setDisplaySnameForm] = useState('none')
	const [newSnameButtonIsDisabled, setNewSnameButtonIsDisabled] =
		useState(false)

	const [canDeleteNotification, setCanDeleteNotification] = useState(null)
	const [nameNotification, setNameNotification] = useState(null)
	const [locationNotification, setLocationNotification] = useState(null)
	const [deleteCreatedSname, setDeleteCreatedSname] = useState(false)
	const [amendMode, setAmendMode] = useState(false)

	useEffect(() => {
		initServer()
		const serverData = loadServerData()
		const map = {}
		serverData.names.forEach(v => (map[v.id] = v))
		serverData.locations.forEach(v => (map[v.id] = v))
		serverData.qualifier_names.forEach(v => (map[v.id] = v))
		serverData.qualifiers.forEach(v => (map[v.id] = v))
		serverData.structured_names.forEach(v => {
			map[v.id] = v
			v.formattedName = formatStructuredName(v, { map })
		})
		serverData.references.forEach(v => (map[v.id] = v))

		if (serverData.amendInfo.amend) {
			setAmendMode(true)
			serverData.amendInfo.relations.forEach(v => map[v.id] = v)
		}

		dispatch(initMapvalues(map))

		if (serverData.amendInfo.amend) {
			const reference = map[serverData.amendInfo.referenceId]
			dispatch(addRef({
				...reference,
				firstAuthor: reference.first_author
			}))
			serverData.amendInfo.relations.forEach(v => {
				dispatch(selectStructuredName(v.name1))
				dispatch(selectStructuredName(v.name2))
			})
			serverData.amendInfo.relations.forEach(v => dispatch(addRel(v)))
		}
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

	const canDeleteNotify = (message, type = 'error') => {
		setCanDeleteNotification({ message, type })
		setTimeout(() => {
			setCanDeleteNotification(null)
		}, 6000)
	}

	const nameNotify = (message, type = 'error') => {
		setNameNotification({ message, type })
		setTimeout(() => {
			setNameNotification(null)
		}, 8000)
	}

	const locationNotify = (message, type = 'error') => {
		setLocationNotification({ message, type })
		setTimeout(() => {
			setLocationNotification(null)
		}, 14000)
	}

	const [addSnameFocus, setAddSnameFocus] = useState(0)

	const addSnameRef = useRef(null)
	const setFocusOnSnameButton = () => {
		setAddSnameFocus(addSnameFocus + 1)
	}
	useEffect(() => {
		if (addSnameFocus > 0 && addSnameRef.current)
			addSnameRef.current.focus()
	}, [addSnameFocus])

	return (
		<>
			<h2>
				<b>{amendMode ? 'Amend Reference' : 'Data Entry'}</b>
			</h2>
			<h3>
				<b>Reference</b>
			</h3>
			<div className='w3-panel w3-padding-24 w3-light-grey'>
				<div className=' w3-container'>
					{state.ref.length === 0 ? (
						<ReferenceForm
							{...{
								displayRefForm,
								showNewReferenceForm,
								setFocusOnSnameButton,
							}}
						/>
					) : (
						state.ref.map(reference =>
							amendMode
								? <ReferenceDisplay
									key={reference.id}
									reference={reference}
								/>
								: (reference.edit
									? <ReferenceForm
										key={reference.id}
										reference={reference}
										displayRefForm={displayRefForm}
										showNewReferenceForm={showNewReferenceForm}
										isQueried={true}
									/>
									: <Reference
										{...{
											key: reference.id,
											reference,
											showNewReferenceForm,
											setFocusOnSnameButton,
										}}
									/>
								)
						)
					)}
				</div>
			</div>
			<h3>
				<b>Structured Names</b>
			</h3>
			<div className='w3-panel w3-padding-24 w3-light-grey'>
				<Notification notification={canDeleteNotification} />
				<Notification notification={nameNotification} />
				<Notification notification={locationNotification} />
				{state.sname.map(sname => (
					<Sname
						{...{ key: sname.id, sname }}
						canDeleteNotify={canDeleteNotify}
						nameNotify={nameNotify}
						locationNotify={locationNotify}
						setDeleteCreatedSname={setDeleteCreatedSname}
					/>
				))}
				<SnameForm
					{...{
						displaySnameForm,
						showNewSnameForm,
						newSnameButtonIsDisabled,
						setNewSnameButtonIsDisabled,
						setFocusOnSnameButton,
						displayRefForm,
						deleteCreatedSname,
						setDeleteCreatedSname,
					}}
				/>
				<div className='w3-container'>
					{newSnameButtonIsDisabled ? (
						<></>
					) : (
							<button
								className='w3-button w3-grey'
								onClick={showNewSnameForm}
								disabled={newSnameButtonIsDisabled}
								id='sname-button'
								ref={addSnameRef}
							>
								Add new structured name
							</button>
					)}
					<hr className='w3-border-top w3-border-grey' />
					<SelectedStructuredNames />
				</div>
			</div>
			<RelationSelector />
			<Submit />
		</>
	)
}

export default App
