import React from 'react';
import './SummaryCards.css';

function SummaryCards({ summary }) {
  const cards = [
    {
      title: 'Total Events',
      value: summary.total_events,
      icon: '📊',
    },
    {
      title: 'Current Occupancy',
      value: summary.current_occupancy,
      subtitle: `/ ${summary.total_devices} slots`,
      icon: '🚗',
    },
    {
      title: 'Active Devices',
      value: summary.active_devices,
      subtitle: `/ ${summary.total_devices} devices`,
      icon: '📡',
      status: summary.active_devices === summary.total_devices ? 'good' : 'warning',
    },
    {
      title: 'Alerts Today',
      value: summary.alerts_today,
      subtitle: `${summary.critical_alerts} critical`,
      icon: '⚠️',
      status: summary.critical_alerts > 0 ? 'critical' : 'good',
    },
  ];

  return (
    <div className="summary-cards">
      {cards.map((card, index) => (
        <div key={index} className={`card ${card.status || ''}`}>
          <div className="card-icon">{card.icon}</div>
          <div className="card-content">
            <h3>{card.title}</h3>
            <div className="card-value">{card.value}</div>
            {card.subtitle && <div className="card-subtitle">{card.subtitle}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

export default SummaryCards;