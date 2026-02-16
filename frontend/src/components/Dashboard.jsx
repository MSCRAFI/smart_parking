import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { format } from 'date-fns';
import { POLLING_INTERVAL } from '../config';
import SummaryCards from './SummaryCards';
import ZoneTable from './ZoneTable';
import './Dashboard.css';

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    try {
      const response = await dashboardAPI.getSummary(selectedDate);
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, POLLING_INTERVAL);
    return () => clearInterval(interval);
  }, [selectedDate]);

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Smart Parking Monitoring</h1>
        <div className="date-picker">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            max={format(new Date(), 'yyyy-MM-dd')}
          />
        </div>
      </div>

      <SummaryCards summary={data.summary} />
      <ZoneTable zones={data.zones} />

      <div className="last-updated">
        Last updated: {format(new Date(data.timestamp), 'HH:mm:ss')}
      </div>
    </div>
  );
}

export default Dashboard;