/**
 * Top-level reducer
 **/
import { fromJS } from 'immutable';
import { combineReducers } from 'redux-immutable';
import { LOCATION_CHANGE } from 'react-router-redux';


/*
 * Reducer for routing
 */
function routeReducer(state, action) {
  if (state === undefined) {
    return fromJS({ location: null });
  }
  switch (action.type) {
    case LOCATION_CHANGE:
      return state.merge({
        location: action.payload
      });
    default:
      return state;
  }
}


/*
 * Top-level reducer for the whole app.
 */
export default function createReducer() {
  return combineReducers({
    route: routeReducer,
  });
}

