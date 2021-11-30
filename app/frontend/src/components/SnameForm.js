import React, { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { parseId, makeId } from '../utilities'
import { addName } from '../store/names/actions'
import { addSname } from '../store/snames/actions'
import { Datalist } from './Datalist'
import {
	selectAllLocations,
	selectAllNames,
	selectMap,
	selectRefence,
} from '../store/snames/selectors'
import { selectStructuredName } from '../store/selected_structured_names/actions'
import { Notification } from './Notification'
import { DuplicateNameDialog } from './DuplicateNameDialog'
import { findDuplicateStructuredNames } from '../utilities'

const NameDataList = React.forwardRef(
	({ name, names, onChangeHandler }, ref) => {
		return(
			<Datalist
				name='name'
				options={names}
				value={name}
				onChange={onChangeHandler}
				innerRef={ref}
			/>
		)
	}
)

export const SnameForm = ({
	displaySnameForm,
	showNewSnameForm,
	newSnameButtonIsDisabled,
	setNewSnameButtonIsDisabled,
	setFocusOnSnameButton,
	displayRefForm,
	deleteCreatedSname,
	setDeleteCreatedSname
}) => {
	const dispatch = useDispatch()
	const reference = useSelector(selectRefence)
	const [name, setName] = useState('')
	const [location, setLocation] = useState('')
	const [qualifier, setQualifier] = useState('')
	const [notification, setNotification] = useState(null)
	const [saveWithReference, setSaveWithReference] = useState(false)
	const [structuredName, setStructuredName] = useState(undefined)

	const map = useSelector(selectMap)
	const names = useSelector(selectAllNames)
	const structuredNames = useSelector(v => v.sname)

	const qualifiers = useSelector(v => {
		return Object.entries(v.map)
			.filter(([key]) => parseId(key).type === 'db_qualifier')
			.map(v => [v[1].id, map[v[1].qualifier_name_id].name])
	})

	const notify = (message, type = 'error') => {
		setNotification({ message, type })
		setTimeout(() => {
			setNotification(null)
		}, 7000)
	}

	const locations = useSelector(selectAllLocations)

	const handleSnameAddition = () => {
		if (!reference) {
			notify('Enter reference before saving a structured name.')
			return
		}

		const qualifierFromDb = qualifiers.find(
			dbQualifier => dbQualifier[1] === qualifier
		)

		if (!qualifierFromDb) {
			notify('Choose a qualifier from the dropdown menu.')
			setQualifier('')
			return
		}
		let nameId, locationId
		if (!names.find(v => v[1] === name)) {
			nameId = makeId('name')
			dispatch(addName({ id: nameId, name: name, variant: 'name' }))
		}

		if (!locations.find(v => v[1] === location)) {
			locationId = makeId('location')
			dispatch(
				addName({ id: locationId, name: location, variant: 'location' })
			)
		}

		const newSname = {
			id: makeId('structured_name'),
			name_id: nameId || names.find(dbName => dbName[1] === name)[0],
			location_id:
				locationId ||
				locations.find(dbLocation => dbLocation[1] === location)[0],
			qualifier_id: qualifierFromDb[0],
			reference_id: -1,
			remarks: '',
			save_with_reference_id: saveWithReference,
		}

		if (
			findDuplicateStructuredNames(newSname, structuredNames).length === 0
		)
			submitSname(newSname)
		else setStructuredName(newSname)
		}

	const submitSname = newSname => {
		dispatch(addSname(newSname))
		dispatch(selectStructuredName(newSname.id))
		hideForm()
	}

	const hideForm = () => {
		setName('')
		setQualifier('')
		setLocation('')
		setStructuredName(undefined)
		showNewSnameForm()
		setNewSnameButtonIsDisabled(!newSnameButtonIsDisabled)
		setFocusOnSnameButton()
	}

	const nameRef = useRef(null)
	useEffect(() => {
		if(newSnameButtonIsDisabled){
			nameRef.current.focus()
		}

		if (displayRefForm === 'none') {
			setFocusOnSnameButton()
		}

		if (displaySnameForm === 'block' && newSnameButtonIsDisabled) {
			nameRef.current.focus()
		}
	}, [newSnameButtonIsDisabled])

	useEffect(() => {
		if(displayRefForm === 'none' && newSnameButtonIsDisabled) {
			nameRef.current.focus()
		}
	}, [displayRefForm])

	useEffect(() => {
		if(displaySnameForm === 'block' && newSnameButtonIsDisabled) {
			nameRef.current.focus()
		}
	}, [displaySnameForm])

	useEffect(() => {
		if(deleteCreatedSname) {
			nameRef.current.focus()
			setDeleteCreatedSname(false)
		}
	}, [deleteCreatedSname])

	if (structuredName !== undefined) {
		const duplicateNames = findDuplicateStructuredNames(
			structuredName,
			structuredNames
		)
		const selectHandler = sname => {
			if (sname.id === structuredName.id) {
				submitSname(sname)
			} else {
				dispatch(selectStructuredName(sname.id))
			}
			hideForm()
		}

		return (
			<DuplicateNameDialog
				{...{
					structuredName,
					duplicateNames,
					selectHandler,
					cancelHandler: hideForm,
				}}
			/>
		)
	}

	return (
		<div style={{ display: displaySnameForm }}>
			<Notification notification={notification} />
			<label htmlFor='name'>Name</label>
			<NameDataList
				ref={nameRef}
				name={name}
				names={names}
				onChangeHandler={e => setName(e.target.value)}
			/>
			<label htmlFor='qualifier'>Qualifier</label>
			<Datalist
				name='qualifier'
				options={qualifiers}
				value={qualifier}
				onChange={e => setQualifier(e.target.value)}
			/>
			<label htmlFor='location'>Location</label>
			<Datalist
				name='location'
				options={locations}
				value={location}
				onChange={e => setLocation(e.target.value)}
			/>
			<input
				type='checkbox'
				id='structured-name-form-save-with-reference'
				checked={saveWithReference}
				onChange={e => setSaveWithReference(!saveWithReference)}
			/>
			<label htmlFor='structured-name-form-save-with-reference'>
				Save with reference id
			</label>
			<button type='button' onClick={() => {
				handleSnameAddition()
				setFocusOnSnameButton()}}>
				Save
			</button>
		</div>
	)
}
