
// Actions
export const CHANGE_SEARCH_TERM = 'FindRoutePage/CHANGE_SEARCH_TERM';
export const START_ROUTE_SEARCH = 'FindRoutePage/START_ROUTE_SEARCH';
export const SEARCH_STARTED = 'FindRoutePage/SEARCH_STARTED';
export const SEARCH_COMPLETED = 'FindRoutePage/SEARCH_COMPLETED';
export const LOAD_MORE_SEARCH_RESULTS = 'FindRoutePage/LOAD_MORE_SEARCH_RESULTS';
export const LOAD_NEXT_STARTED = 'FindRoutePage/LOAD_NEXT_STARTED';
export const LOAD_NEXT_COMPLETED = 'FindRoutePage/LOAD_NEXT_COMPLETED';


export function changeSearchTerm(term) {
  return {
    type: CHANGE_SEARCH_TERM,
    searchTerm: term,
  };
}

export function startSearch() {
  return {
    type: START_ROUTE_SEARCH
  };
}

export function searchStarted() {
  return {
    type: SEARCH_STARTED,
  }
};

export function searchCompleted(results) {
  return {
    type: SEARCH_COMPLETED,
    results: results['results'],
    resultCount: results['count'],
    nextUrl: results['next'],
  };
}

export function loadMoreSearchResults() {
  return {
    type: LOAD_MORE_SEARCH_RESULTS,
  };
}

export function loadNextStarted() {
  return {
    type: LOAD_NEXT_STARTED,
  };
}

export function loadNextCompleted(results) {
  return {
    type: LOAD_NEXT_COMPLETED,
    results: results['results'],
    nextUrl: results['next'],
  };
}
