import React from 'react';
import Dashboard from './components/Dashboard';
import AlertPanel from './components/AlertPanel';
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
      <AlertPanel />
    </div>
  );
}

export default App;