
import { fromJS } from 'immutable';

import {
  CHANGE_SEARCH_TERM,
  START_ROUTE_SEARCH,
  SEARCH_STARTED,
  SEARCH_COMPLETED,
} from './actions';

const initialState = fromJS({
  searchTerm: '',
  searchInProgress: false,
  searchResults: [],
});

export function findRoutePageReducer(state = initialState, action) {
  switch (action.type) {
    case CHANGE_SEARCH_TERM:
      return state.set('searchTerm', action.searchTerm);
    case SEARCH_STARTED:
      return state.set('searchInProgress', true);
    case SEARCH_COMPLETED:
      return state.set('searchInProgress', false).set('searchResults', action.results);
    default:
      return state;
  }
}
