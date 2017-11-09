
// Actions
export const CHANGE_SEARCH_TERM = 'FindRoutePage/CHANGE_SEARCH_TERM';
export const START_ROUTE_SEARCH = 'FindRoutePage/START_ROUTE_SEARCH';
export const SEARCH_STARTED = 'FindRoutePage/SEARCH_STARTED';
export const SEARCH_COMPLETED = 'FindRoutePage/SEARCH_COMPLETED';


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
    nextUrl: results['next']
  };
}
