import { createStore, combineReducers, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import { composeWithDevTools } from 'redux-devtools-extension'
import { refReducer } from './references/reducers'
import { snameReducer } from './snames/reducers'
import { relReducer } from './relations/reducers'
import { mapReducer } from './map/reducers'
import { nameReducer } from './names/reducers'

const devTools =
	process.env.NODE_ENV === 'production'
		? applyMiddleware(thunk)
		: composeWithDevTools(applyMiddleware(thunk))

export const store = createStore(
	combineReducers({
		ref: refReducer,
		sname: snameReducer,
		rel: relReducer,
		map: mapReducer,
		names: nameReducer,
	}),
	devTools
)

export default store
