import React from 'react';

export default function AlertsPanel() {
  const alerts = [
    { id: 1, type: 'critical', title: 'Threshold Exceeded: Sector 4', time: '10 mins ago', desc: 'Wet bulb temperature exceeded 32°C limit.' },
    { id: 2, type: 'warning', title: 'Heat Advisory: Plant Wide', time: '1 hour ago', desc: 'Solar radiation peak expected at 14:00.' },
    { id: 3, type: 'info', title: 'Sensor Calibration', time: '3 hours ago', desc: 'Routine calibration completed for Node Alpha.' },
  ];

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg flex flex-col h-full relative">
      <span className="absolute top-3 right-3 text-[10px] font-bold tracking-wider text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
        DEMO
      </span>
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-sm font-semibold text-gray-200">System Alerts</h3>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {alerts.map(alert => (
          <div key={alert.id} className="p-3 bg-gray-950 border border-gray-800 rounded-md">
            <div className="flex justify-between items-start mb-1">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  alert.type === 'critical' ? 'bg-risk-extreme shadow-[0_0_5px_rgba(239,68,68,0.8)]' : 
                  alert.type === 'warning' ? 'bg-risk-moderate shadow-[0_0_5px_rgba(245,158,11,0.8)]' : 'bg-blue-500'
                }`}></div>
                <h4 className="text-xs font-semibold text-gray-300">{alert.title}</h4>
              </div>
              <span className="text-[10px] text-gray-600 whitespace-nowrap">{alert.time}</span>
            </div>
            <p className="text-xs text-gray-500 ml-4">{alert.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
