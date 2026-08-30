import React from 'react';
import { DataProvenance } from '@/types';

interface RiskCardProps {
  level: 'Low' | 'Moderate' | 'High' | 'Extreme';
  provenance?: DataProvenance;
}

export default function RiskCard({ level, provenance = 'demo_synthetic' }: RiskCardProps) {
  const getRiskDetails = () => {
    switch(level) {
      case 'Low': return { color: 'text-risk-low', bg: 'bg-risk-low', text: 'Normal Industrial Conditions', border: 'border-risk-low/30' };
      case 'Moderate': return { color: 'text-risk-moderate', bg: 'bg-risk-moderate', text: 'Hydration & Monitor Shifts', border: 'border-risk-moderate/30' };
      case 'High': return { color: 'text-risk-high', bg: 'bg-risk-high', text: 'Enforce Work-Rest Schedules', border: 'border-risk-high/30' };
      case 'Extreme': return { color: 'text-risk-extreme', bg: 'bg-risk-extreme', text: 'Mandatory Shaded Rest / Cool Zones', border: 'border-risk-extreme/30' };
      default: return { color: 'text-gray-500', bg: 'bg-gray-500', text: 'Awaiting Assessment', border: 'border-gray-800' };
    }
  };

  const details = getRiskDetails();

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
    <div className={`bg-gray-900 border ${details.border} rounded-lg p-6 relative overflow-hidden flex flex-col justify-center h-full`}>
      <div className={`absolute top-0 left-0 w-full h-1 ${details.bg}`}></div>
      
      {getProvenanceBadge()}
      
      <h3 className="text-xs font-medium text-gray-400 mb-2 uppercase tracking-widest">Site Thermal Severity</h3>
      
      <div className="flex items-center gap-4 mt-2">
        <div className={`p-4 rounded-full bg-gray-950 border border-gray-800 flex items-center justify-center ${details.color} shadow-[0_0_15px_rgba(0,0,0,0.5)]`}>
          <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        
        <div>
          <div className={`text-3xl font-bold ${details.color}`}>{level}</div>
          <div className="text-xs font-medium text-gray-300 mt-1">{details.text}</div>
        </div>
      </div>
    </div>
  );
}
