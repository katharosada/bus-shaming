import { call, put, select, takeLatest } from 'redux-saga/effects';
import request from '../../utils/request';

import {
  LOAD_ROUTE,
  loadRouteStarted,
  loadRouteCompleted,
} from './actions';


export function* loadRoute() {
  const state = yield select();
  const routeId = state.get('RoutePage').get('currentRouteId');

  const url = process.env.API_URL + '/routes/' + routeId + '/';
  yield put(loadRouteStarted());

  try {
    const results = yield call(request, url);
    yield put(loadRouteCompleted(results));
  } catch (err) {
    // TODO: Handle error nicely here.
    console.warn(err);
  }
}

export function* routePageSagas() {
  yield takeLatest(LOAD_ROUTE, loadRoute);
};
