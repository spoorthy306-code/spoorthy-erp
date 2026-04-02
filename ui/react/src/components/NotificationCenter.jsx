import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = () => {
    axios.get('/api/notifications/unread').then(res => setNotifications(res.data || []));
  };

  const markRead = id => axios.post(`/api/notifications/${id}/read`).then(fetchNotifications);

  return (
    <div>
      <h2>Notifications</h2>
      <ul>{notifications.map(n => <li key={n.id}>{n.message} <button onClick={() => markRead(n.id)}>Mark Read</button></li>)}</ul>
    </div>
  );
}
