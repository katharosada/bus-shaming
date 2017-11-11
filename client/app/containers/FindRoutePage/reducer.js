
import { fromJS, List } from 'immutable';

import {
  CHANGE_SEARCH_TERM,
  START_ROUTE_SEARCH,
  SEARCH_STARTED,
  SEARCH_COMPLETED,
  LOAD_NEXT_STARTED,
  LOAD_NEXT_COMPLETED,
} from './actions';

const initialState = fromJS({
  searchTerm: '',
  searchInProgress: false,
  searchResults: null,
  nextUrl: null,
  loadNextInProgress: false,
  resultCount: 0,
});

export function findRoutePageReducer(state = initialState, action) {
  switch (action.type) {
    case CHANGE_SEARCH_TERM:
      return state.set('searchTerm', action.searchTerm);
    case SEARCH_STARTED:
      return state.merge({
        'searchInProgress': true,
        'nextUrl': null,
      });
    case SEARCH_COMPLETED:
      return state.merge({
        'searchInProgress': false,
        'searchResults': action.results,
        'nextUrl': action.nextUrl,
        'resultCount': action.resultCount,
      });
    case LOAD_NEXT_STARTED:
      return state.merge({
        loadNextInProgress: true,
        nextUrl: null,
      });
    case LOAD_NEXT_COMPLETED:
      const newResults = state.get('searchResults').push(...fromJS(action.results));
      return state.merge({
        searchResults: newResults,
        loadNextInProgress: false,
        nextUrl: action.nextUrl,
      });
    default:
      return state;
  }
}
