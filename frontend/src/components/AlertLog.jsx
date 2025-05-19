import { useEffect, useState } from 'react';
import axios from 'axios';

const AlertLog = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/recent-alerts')
      .then((res) => {
        setAlerts(res.data);
      })
      .catch((err) => {
        console.error("Failed to fetch alerts:", err);
      });
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
      {alerts.map((alert, index) => (
        <div key={index} className="bg-white rounded-lg shadow-lg p-4">
          <img
            src={`http://localhost:8000${alert.image_url}`}
            alt="Detection"
            className="rounded-md mb-3"
          />
          <p className="text-gray-800 font-semibold">
            🕒 {new Date(alert.timestamp).toLocaleString()}
          </p>
          <p className="text-gray-600">📍 {alert.location}</p>
        </div>
      ))}
    </div>
  );
};

export default AlertLog;
