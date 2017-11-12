
export const LOAD_ROUTE = 'RoutePage/LOAD_ROUTE';
export const LOAD_ROUTE_STARTED = 'RoutePage/LOAD_ROUTE_STARTED';
export const LOAD_ROUTE_COMPLETED = 'RoutePage/LOAD_ROUTE_COMPLETED';

export function loadRoute(id) {
  return {
    type: LOAD_ROUTE,
    routeId: id,
  };
}

export function loadRouteStarted() {
  return {
    type: LOAD_ROUTE_STARTED,
  };
}

export function loadRouteCompleted(result) {
  return {
    type: LOAD_ROUTE_COMPLETED,
    route: result,
  };
}
