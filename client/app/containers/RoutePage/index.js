import React from 'react';
import { connect } from 'react-redux';
import { compose } from 'redux';

import {
  loadRoute,
} from './actions';

function RouteDisplay(props) {
  const route = props.route;
  return <div>
    <h1>Bus route { route.get('short_name') }</h1>
    <p>{ route.get('long_name') }</p>
    <p>{ route.get('description') }</p>
    <h3>Last two weeks:</h3>
    {
      route.get('recent_dates').map((route_date) => {
        let ontime = (100 * route_date.get('trip_ontime_percent')).toFixed(1) + '%';
        return <p key={route_date.get('id')}>{route_date.get('date')} - {ontime} of trips were on-time</p>;
      })
    }
  </div>
}

class RoutePage extends React.PureComponent {

  componentDidMount() {
    const route_id = this.props.match.params.id;
    if (this.props.route === null || this.props.route.id !== route_id) {
      this.props.onPageLoad(route_id);
    }
  }

  render() {
    const route_id = this.props.match.params.id;
    if (this.props.route !== null && !this.props.loadInProgress) {
      return <div className="column">
        <RouteDisplay route={this.props.route} />
      </div>;
    }
    return <div className="column">
      <p>Loading...</p>
    </div>;
  }
};

const mapStateToProps = function(state) {
  const localState = state.get('RoutePage');
  return {
    route: localState.get('route'),
    loadInProgress: localState.get('routeLoadInProgress'),
  };
};

const mapDispatchToProps = function(dispatch) {
  return {
    onPageLoad: (id) => {
      dispatch(loadRoute(id));
    },

  };
};

export default compose(
  connect(mapStateToProps, mapDispatchToProps)
)(RoutePage);
