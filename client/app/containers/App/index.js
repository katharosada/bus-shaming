import React from 'react';
import { Switch, Route, Link } from 'react-router-dom';

import HomePage from '../HomePage/index';
import FindRoutePage from '../FindRoutePage/index';

/**
 * Base page for the whole app, includes menus, header, footer and routing.
 **/
export default function App() {
  return (
      <div>
        <header>
          <Link to="/">Home</Link>
          <Link to="/find">FindRoute</Link>
        </header>
        <Switch>
          <Route exact path="/" component={HomePage} />
          <Route path="/find" component={FindRoutePage} />
        </Switch>
      </div>
    );
};
