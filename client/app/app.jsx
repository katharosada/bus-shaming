import { fromJS } from 'immutable';
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compse } from 'redux';
import 'regenerator-runtime/runtime';
import createSagaMiddleware from 'redux-saga';
import { ConnectedRouter, routerMiddleware } from 'react-router-redux';
import createHistory from 'history/createBrowserHistory';

import { findRoutePageSagas } from './containers/FindRoutePage/sagas';
import { routePageSagas } from './containers/RoutePage/sagas';
import App from './containers/App/index';
import createReducer from './reducers';

import './app.less';

const sagaMiddleware = createSagaMiddleware();

function configureStore(initialSate, history) {
  const middleware = [
    sagaMiddleware,
    routerMiddleware(history),
  ];

  const store = createStore(
    createReducer(),
    fromJS(initialState),
    applyMiddleware(...middleware)
  );
  sagaMiddleware.run(findRoutePageSagas);
  sagaMiddleware.run(routePageSagas);
  return store;
};



const initialState = {};
const history = createHistory();
const store = configureStore(initialState, history);


ReactDOM.render(
  <Provider store={store}>
    <ConnectedRouter history={history}>
      <App />
    </ConnectedRouter>
  </Provider>,
  document.getElementById('app')
);

