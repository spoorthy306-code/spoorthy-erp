import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function Dashboard() {
  const [kpis, setKpis] = useState({});
  const [trend, setTrend] = useState([]);

  useEffect(() => {
    axios.get('/api/dashboard/kpis').then(res => setKpis(res.data));
    axios.get('/api/dashboard/sales_trend').then(res => setTrend(res.data.trend || []));
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Total Sales: {kpis.total_sales}</p>
      <LineChart width={600} height={300} data={trend}>
        <XAxis dataKey="day" />
        <YAxis />
        <CartesianGrid strokeDasharray="3 3" />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="sales" stroke="#8884d8" />
      </LineChart>
    </div>
  );
}
