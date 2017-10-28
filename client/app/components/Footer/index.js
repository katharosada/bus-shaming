import React from 'react';
import { Link } from 'react-router-dom';

import './styles.less';

/**
 * Footer component.
 **/
export default function Header() {
  return (
      <footer id="main-footer">
        <div className="column">
          Made by <a href="https://katiebell.net">Katie Bell</a>
        </div>
      </footer>
    );
};
