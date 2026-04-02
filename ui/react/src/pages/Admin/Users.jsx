import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    axios.get('/api/admin/users').then(res => { setUsers(res.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1>Users</h1>
      {loading ? <p>Loading...</p> : <ul>{users.map(u => <li key={u.id}>{u.name} ({u.email})</li>)}</ul>}
    </div>
  );
}
