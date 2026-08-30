import React from 'react';
import { DataProvenance } from '@/types';

interface MetricCardProps {
  title: string;
  value: number | null;
  unit: string;
  icon: React.ReactNode;
  colorClass: string;
  provenance?: DataProvenance;
}

export default function MetricCard({
  title,
  value,
  unit,
  icon,
  colorClass,
  provenance = 'demo_synthetic'
}: MetricCardProps) {
  const getProvenanceBadge = () => {
    switch (provenance) {
      case 'raw_fortyguard':
        return (
          <span className="absolute top-3 right-3 text-[9px] font-bold tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
            RAW FORTYGUARD
          </span>
        );
      case 'derived':
        return (
          <span className="absolute top-3 right-3 text-[9px] font-bold tracking-wider text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
            DERIVED
          </span>
        );
      case 'simulated':
        return (
          <span className="absolute top-3 right-3 text-[9px] font-bold tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/30">
            SIMULATED
          </span>
        );
      case 'demo_synthetic':
      default:
        return (
          <span className="absolute top-3 right-3 text-[9px] font-bold tracking-wider text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
            SYNTHETIC DEMO
          </span>
        );
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-5 relative overflow-hidden group">
      {/* Top accent line */}
      <div className={`absolute top-0 left-0 w-full h-1 ${colorClass}`}></div>
      
      {getProvenanceBadge()}
      
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-md bg-gray-800 border border-gray-700 ${colorClass.replace('bg-', 'text-')}`}>
          {icon}
        </div>
        <h3 className="text-sm font-medium text-gray-400">{title}</h3>
      </div>
      
      <div className="flex items-baseline gap-1 mt-2">
        {value !== null && value !== undefined ? (
          <>
            <span className="text-3xl font-bold text-gray-100">{value.toFixed(1)}</span>
            <span className="text-sm font-medium text-gray-500">{unit}</span>
          </>
        ) : (
          <span className="text-3xl font-bold text-gray-600">N/A</span>
        )}
      </div>
    </div>
  );
}
