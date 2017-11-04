import { call, put, select, takeLatest } from 'redux-saga/effects';

import {
  START_ROUTE_SEARCH,
  searchStarted,
  searchCompleted,
} from './actions';


function delay(ms) {
    return new Promise(resolve => setTimeout(() => resolve(true), ms))
}

export function* search() {
  const state = yield select();
  const searchTerm = state.get('FindRoutePage').get('searchTerm');

  yield put(searchStarted());

  const results = ['search result1', 'search result2'];
  const done = yield call(delay, 5000);
  yield put(searchCompleted(results));
}

export function* findRoutePageSagas() {
  yield takeLatest(START_ROUTE_SEARCH, search);
};

