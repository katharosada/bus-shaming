import React from 'react';


export function StopSequenceDisplay(props) {
  const sequence = props.sequence;
  return (<p>
      { sequence.get('trip_short_name') } ({ sequence.get('length') } stops)
      <br/>
  </p>);
}
