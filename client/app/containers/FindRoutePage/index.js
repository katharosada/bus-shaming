import React from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { compose } from 'redux';

import { changeSearchTerm, loadMoreSearchResults, startSearch } from './actions';
import { RouteSearchResults } from '../../components/SearchResults/index';

/*
 * Find route page component
 */
function FindRoutePage(props) {

  let results = <p></p>
  if (props.inProgress) {
    results = <p>Loading...</p>
  }
  if (props.searchResults !== null) {
    results = <RouteSearchResults
          searchResults={ props.searchResults }
          resultCount={ props.resultCount }
        />
  }

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
        { results }
        {
          props.loadNextInProgress ?
            <p>Loading...</p>
          :
            null
        }
        {
          props.nextUrl !== null ?
            <div>
              <button onClick={props.onClickLoadMore}>Load more</button>
            </div>
          :
            null
        }
        <p>&nbsp;</p>
      </div>
  );
};

const mapStateToProps = function(state) {
  const localState = state.get('FindRoutePage');
  return {
    searchTerm: localState.get('searchTerm'),
    inProgress: localState.get('searchInProgress'),
    searchResults: localState.get('searchResults'),
    resultCount: localState.get('resultCount'),
    nextUrl: localState.get('nextUrl'),
    loadNextInProgress: localState.get('loadNextInProgress'),
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
    onClickLoadMore: (evt) => {
      dispatch(loadMoreSearchResults());
    }
  };
};

export default compose(
  connect(mapStateToProps, mapDispatchToProps)
)(FindRoutePage);
