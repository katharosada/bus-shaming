import { fromJS } from 'immutable';
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compse } from 'redux';
import createSagaMiddleware from 'redux-saga';
import { ConnectedRouter, routerMiddleware } from 'react-router-redux';
import createHistory from 'history/createBrowserHistory';

import App from './containers/App/index';
import createReducer from './reducers';

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

