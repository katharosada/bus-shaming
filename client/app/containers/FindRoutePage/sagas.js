import { call, put, select, takeLatest } from 'redux-saga/effects';

import request from '../../utils/request';

import {
  START_ROUTE_SEARCH,
  LOAD_MORE_SEARCH_RESULTS,
  searchStarted,
  searchCompleted,
  loadNextStarted,
  loadNextCompleted,
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

export function* loadNext() {
  const state = yield select();
  const nextUrl = state.get('FindRoutePage').get('nextUrl');
  if (nextUrl === null) {
    return;
  }
  yield put(loadNextStarted());
  try {
    const results = yield call(request, nextUrl);
    yield put(loadNextCompleted(results));
  } catch (err) {
    // TODO: Handle search error nicely here.
    console.warn(err);
  }
}

export function* findRoutePageSagas() {
  yield takeLatest(START_ROUTE_SEARCH, search);
  yield takeLatest(LOAD_MORE_SEARCH_RESULTS, loadNext);
};

