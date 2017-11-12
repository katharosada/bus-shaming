import { fromJS, List } from 'immutable';

import {
  LOAD_ROUTE,
  LOAD_ROUTE_STARTED,
  LOAD_ROUTE_COMPLETED,
} from './actions';


const initialState = fromJS({
  currentRouteId: null,
  route: null,
  routeLoadInProgress: false,
});

export function routePageReducer(state = initialState, action) {
  switch(action.type) {
    case LOAD_ROUTE:
      return state.set('currentRouteId', action.routeId);
    case LOAD_ROUTE_STARTED:
      return state.set('routeLoadInProgress': true);
    case LOAD_ROUTE_COMPLETED:
      return state.merge({
        routeLoadInProgress: false,
        route: action.route,
      });
    default:
      return state;
  }
};
