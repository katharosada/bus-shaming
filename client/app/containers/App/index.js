import React from 'react';
import { Switch, Route, Link } from 'react-router-dom';

import HomePage from '../HomePage/index';
import FindRoutePage from '../FindRoutePage/index';
import Header from '../../components/Header/index.js';
import Footer from '../../components/Footer/index.js';

/**
 * Base page for the whole app, includes menus, header, footer and routing.
 **/
export default function App() {
  return (
      <div className="container">
        <div id="page-container">
          <Header />
          <Switch>
            <Route exact path="/" component={HomePage} />
            <Route path="/find" component={FindRoutePage} />
          </Switch>
        </div>
        <Footer />
      </div>
    );
};
