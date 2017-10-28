import React from 'react';
import { Link } from 'react-router-dom';

import './styles.less';

/**
 * Header component.
 **/
export default function Header() {
  return (
      <header id="main-header">
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/find">Find</Link></li>
          </ul>
        </nav>
      </header>
    );
};
