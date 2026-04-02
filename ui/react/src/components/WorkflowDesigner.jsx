import React, { useState } from 'react';
import ReactFlow from 'react-flow-renderer';

export default function WorkflowDesigner() {
  const [elements, setElements] = useState([]);

  return (
    <div style={{ height: 500, border: '1px solid #ccc' }}>
      <h2>Workflow Designer</h2>
      <ReactFlow elements={elements} />
      <button onClick={() => { fetch('/api/workflow/validate', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nodes:[],edges:[]})}) }}>Validate</button>
    </div>
  );
}
