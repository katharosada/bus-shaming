import React from 'react';
import { connect } from 'react-redux';
import { compose } from 'redux';

import { changeSearchTerm, startSearch } from './actions';

/*
 * Find route page component
 */
function FindRoutePage(props) {
  return (
      <div className="column">
        <h1>Find a bus route</h1>
        <form onSubmit={props.onSearchSubmit}>
          <input
            type="text"
            name="search"
            value={props.searchTerm}
            onChange={props.onChangeSearchTerm} />
          <input type="submit" value="Search" />
        </form>
        <p>{ props.inProgress ? 'loading...' : '' }</p>
        <p>{props.searchResults}</p>
      </div>
  );
};

const mapStateToProps = function(state) {
  const localState = state.get('FindRoutePage');
  return {
    searchTerm: localState.get('searchTerm'),
    inProgress: localState.get('searchInProgress'),
    searchResults: localState.get('searchResults'),
  };
};

const mapDispatchToProps = function(dispatch) {
  return {
    onSearchSubmit: (evt) => {
      if (evt !== undefined && evt.preventDefault) {
        evt.preventDefault();
      }
      dispatch(startSearch());
    },
    onChangeSearchTerm: (evt) => {
      dispatch(changeSearchTerm(evt.target.value));
    },
  };
};

export default compose(
  connect(mapStateToProps, mapDispatchToProps)
)(FindRoutePage);
