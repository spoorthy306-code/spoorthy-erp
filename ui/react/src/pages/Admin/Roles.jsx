import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Roles() {
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    axios.get('/api/admin/roles').then(res => setRoles(res.data));
  }, []);

  return (
    <div>
      <h1>Roles</h1>
      <ul>{roles.map(r => <li key={r.id}>{r.name}</li>)}</ul>
    </div>
  );
}
