import React, { useState, useEffect } from 'react';
import { alertAPI } from '../services/api';
import { format } from 'date-fns';
import { SEVERITY_COLORS, POLLING_INTERVAL } from '../config';
import './AlertPanel.css';

function AlertPanel() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const params = filter !== 'all' ? { severity: filter } : {};
      const response = await alertAPI.getAlerts(params);
      setAlerts(response.data);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, POLLING_INTERVAL);
    return () => clearInterval(interval);
  }, [filter]);

  const handleAcknowledge = async (alertId) => {
    try {
      await alertAPI.acknowledge(alertId);
      fetchAlerts();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const unacknowledgedAlerts = alerts.filter(a => !a.is_acknowledged);

  return (
    <div className="alert-panel">
      <div className="alert-header">
        <h2>Active Alerts ({unacknowledgedAlerts.length})</h2>
        <div className="alert-filters">
          {['all', 'CRITICAL', 'WARNING', 'INFO'].map(f => (
            <button
              key={f}
              className={`filter-btn ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading alerts...</div>
      ) : (
        <div className="alert-list">
          {alerts.length === 0 ? (
            <div className="no-alerts">No alerts found</div>
          ) : (
            alerts.map(alert => (
              <div
                key={alert.id}
                className={`alert-item ${alert.severity.toLowerCase()} ${
                  alert.is_acknowledged ? 'acknowledged' : ''
                }`}
              >
                <div className="alert-indicator" style={{ 
                  backgroundColor: SEVERITY_COLORS[alert.severity] 
                }} />
                <div className="alert-content">
                  <div className="alert-title">
                    <span className="severity-badge">{alert.severity}</span>
                    <span className="alert-type">{alert.alert_type}</span>
                  </div>
                  <div className="alert-message">{alert.message}</div>
                  <div className="alert-meta">
                    <span>Device: {alert.device_code}</span>
                    <span>Zone: {alert.zone_name}</span>
                    <span>{format(new Date(alert.created_at), 'MMM dd, HH:mm')}</span>
                  </div>
                </div>
                {!alert.is_acknowledged && (
                  <button
                    className="acknowledge-btn"
                    onClick={() => handleAcknowledge(alert.id)}
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default AlertPanel;