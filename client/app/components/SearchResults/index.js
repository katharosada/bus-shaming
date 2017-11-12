import React from 'react';
import { Link } from 'react-router-dom';

import './styles.less';


export function RouteSearchResults(props) {

  return <div>
    <p className="result-count">{ props.resultCount } { props.resultCount === 1 ? 'result' : 'results' }</p>
    {
      props.searchResults.map((result) => {
        const key = result.get('id');
        const style = {
          'backgroundColor': '#' + result.get('color'),
          'color': '#' + result.get('text_color'),
        };
        return <Link key={ key } to={ "route/" + key }>
          <div className="route-result">
            <div className="route-label-box">
              <span className="route-label" style={style}>{ result.get('short_name')}</span>
            </div>
            <div className="route-description">
              <p className="route-name">
                { result.get('long_name') }
              </p>
              <p className="description">
                { result.get('description') }
              </p>
            </div>
          </div>
        </Link>;
      })
    }
    </div>
};
