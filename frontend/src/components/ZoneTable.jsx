import React from 'react';
import './ZoneTable.css';

function ZoneTable({ zones }) {
  const getStatusBadge = (status) => {
    const badges = {
      good: { label: 'Good', color: '#10b981' },
      warning: { label: 'Warning', color: '#f59e0b' },
      poor: { label: 'Poor', color: '#ef4444' },
    };
    const badge = badges[status] || badges.warning;
    
    return (
      <span className="status-badge" style={{ backgroundColor: badge.color }}>
        {badge.label}
      </span>
    );
  };

  return (
    <div className="zone-table-container">
      <h2>Zone Performance</h2>
      <table className="zone-table">
        <thead>
          <tr>
            <th>Zone</th>
            <th>Events</th>
            <th>Target</th>
            <th>Efficiency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {zones.map((zone, index) => (
            <tr key={index}>
              <td>
                <strong>{zone.zone_name}</strong>
                <span className="zone-code"> ({zone.zone_code})</span>
              </td>
              <td>{zone.events}</td>
              <td>{zone.target}</td>
              <td>
                <div className="efficiency-bar">
                  <div 
                    className="efficiency-fill" 
                    style={{ 
                      width: `${Math.min(zone.efficiency, 100)}%`,
                      backgroundColor: zone.status === 'good' ? '#10b981' : 
                                      zone.status === 'warning' ? '#f59e0b' : '#ef4444'
                    }}
                  />
                  <span className="efficiency-text">{zone.efficiency}%</span>
                </div>
              </td>
              <td>{getStatusBadge(zone.status)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ZoneTable;