import { call, put, select, takeLatest } from 'redux-saga/effects';

import request from '../../utils/request';

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

  const url = process.env.API_URL + '/routes/?search=' + encodeURIComponent(searchTerm);
  yield put(searchStarted());

  try {
    const results = yield call(request, url);
    yield put(searchCompleted(results));
  } catch (err) {
    // TODO: Handle search error nicely here.
    console.warn(err);
  }
}

export function* findRoutePageSagas() {
  yield takeLatest(START_ROUTE_SEARCH, search);
};

