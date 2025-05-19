import React, { useState, useEffect } from 'react';
import './App.css'; // Tailwind directives

function App() {
  const [status, setStatus] = useState('🚀 FalconPatrol AI - Spot Dashboard');
  const [logs, setLogs] = useState([]);
  const [yoloLogs, setYoloLogs] = useState([]);  // New state for YOLO logs

  // Fetch system logs every 2 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/logs');
        const { logs } = await res.json();
        setLogs(logs.reverse());
      } catch (err) {
        console.error('Fetch logs error:', err);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch YOLO alert logs every 5 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/yolo/alerts');  // Adjust backend route if needed
        const { alerts } = await res.json();
        setYoloLogs(alerts.reverse());
      } catch (err) {
        console.error('Fetch YOLO alerts error:', err);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCommand = async (action) => {
    setStatus(`⏳ Executing ${action}...`);
    try {
      const res = await fetch(`http://localhost:8000/${action}`);
      if (!res.ok) {
        const { detail } = await res.json();
        throw new Error(detail);
      }
      const { message } = await res.json();
      setStatus(message);
    } catch (err) {
      setStatus(`⚠️ ${err.message}`);
    }
  };

  // New function to trigger YOLO capture
  const handleYoloCapture = async () => {
    setStatus('🎯 Capturing YOLO detection...');
    try {
      const res = await fetch('http://localhost:8000/yolo/capture');  // Adjust route as per your backend
      if (!res.ok) {
        const { detail } = await res.json();
        throw new Error(detail);
      }
      const { message } = await res.json();
      setStatus(message);
    } catch (err) {
      setStatus(`⚠️ YOLO capture error: ${err.message}`);
    }
  };

  const buttons = [
    { action: 'stand', label: '🦾 Stand', color: 'bg-blue-600 hover:bg-blue-700' },
    { action: 'dock', label: '🔋 Dock', color: 'bg-red-600 hover:bg-red-700' },
    { action: 'undock', label: '📦 Undock', color: 'bg-orange-500 hover:bg-orange-600' },
    { action: 'poweroff', label: '🔴 Power Off', color: 'bg-red-800 hover:bg-red-900' }
  ];

  return (
    <div className="min-h-screen bg-zinc-900 text-white p-6">
      <div className="bg-zinc-800 p-6 rounded-xl shadow mb-8">
        <h1 className="text-2xl md:text-3xl font-bold animate-pulse bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
          {status}
        </h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {buttons.map(btn => (
          <button
            key={btn.action}
            onClick={() => handleCommand(btn.action)}
            className={`${btn.color} text-white py-4 px-6 rounded-lg shadow transition transform hover:-translate-y-1`}
          >
            {btn.label}
          </button>
        ))}
        {/* New YOLO capture button */}
        <button
          onClick={handleYoloCapture}
          className="bg-green-600 hover:bg-green-700 text-white py-4 px-6 rounded-lg shadow transition transform hover:-translate-y-1"
        >
          🎯 Capture YOLO
        </button>
      </div>

      {/* System Logs */}
      <div className="bg-zinc-800 p-6 rounded-xl max-h-80 overflow-y-auto mb-8">
        <h3 className="text-xl font-semibold text-blue-400 mb-4">System Logs</h3>
        <div className="space-y-2 font-mono text-sm">
          {logs.map((log, idx) => (
            <div
              key={idx}
              className={`p-2 rounded-md ${
                log.toLowerCase().includes('error') || log.toLowerCase().includes('failed')
                  ? 'bg-red-500 text-white'
                  : 'bg-zinc-700 text-gray-300'
              }`}
            >
              {log}
            </div>
          ))}
        </div>
      </div>

      {/* YOLO Alert Logs */}
      <div className="bg-zinc-800 p-6 rounded-xl max-h-80 overflow-y-auto">
        <h3 className="text-xl font-semibold text-green-400 mb-4">YOLO Alert Log</h3>
        <div className="space-y-4">
          {yoloLogs.length === 0 && <p className="text-gray-400">No YOLO detections yet.</p>}
          {yoloLogs.map((alert, idx) => (
            <div key={idx} className="bg-zinc-700 p-3 rounded-md flex items-center space-x-4">
              <img src={alert.imageUrl} alt="Detection" className="w-24 h-24 object-cover rounded" />
              <div className="text-sm">
                <p><strong>Time:</strong> {alert.time}</p>
                <p><strong>Location:</strong> {alert.location}</p>
                <p><strong>Description:</strong> {alert.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
