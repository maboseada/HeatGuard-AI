"use client";
import React from 'react';
import { WorkloadCategory } from '@/types';

interface Props {
  workload: WorkloadCategory;
  onWorkloadChange: (workload: WorkloadCategory) => void;
  workMinutes: number;
  restMinutes: number;
  hydrationMl: number;
  riskCategory: string;
  warnings: string[];
}

export default function HSEProtocolCard({
  workload,
  onWorkloadChange,
  workMinutes,
  restMinutes,
  hydrationMl,
  riskCategory,
  warnings,
}: Props) {
  const getSeverityBadgeColor = () => {
    switch (riskCategory) {
      case 'Extreme':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'High':
        return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
      case 'Moderate':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden shadow-lg flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 bg-gray-900 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-100">HSE Operational Protocol</h3>
        </div>
        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded border ${getSeverityBadgeColor()}`}>
          {riskCategory.toUpperCase()} SHIFT
        </span>
      </div>

      <div className="p-5 space-y-4 flex-1 flex flex-col justify-between">
        {/* Workload Selector */}
        <div>
          <div className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">Select Worker Exertion:</div>
          <div className="grid grid-cols-3 gap-1.5 bg-gray-950 p-1 rounded-lg border border-gray-800 text-xs">
            {(['Light', 'Moderate', 'Heavy'] as WorkloadCategory[]).map((cat) => (
              <button
                key={cat}
                onClick={() => onWorkloadChange(cat)}
                className={`py-1.5 rounded-md font-semibold transition-all ${
                  workload === cat
                    ? 'bg-amber-500 text-gray-950 shadow-sm'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Work-Rest Visual Bar */}
        <div>
          <div className="flex justify-between text-xs font-medium text-gray-300 mb-1.5">
            <span>Work Cycle ({workMinutes} min)</span>
            <span className="text-amber-400">Rest Cycle ({restMinutes} min)</span>
          </div>
          <div className="w-full h-4 bg-gray-950 rounded-full overflow-hidden flex border border-gray-800 p-0.5">
            <div
              style={{ width: `${(workMinutes / 60) * 100}%` }}
              className="bg-emerald-500 rounded-l-full h-full transition-all duration-300 flex items-center justify-center text-[9px] font-bold text-gray-950"
            >
              {workMinutes > 15 ? `${workMinutes}m` : ''}
            </div>
            <div
              style={{ width: `${(restMinutes / 60) * 100}%` }}
              className="bg-amber-500 rounded-r-full h-full transition-all duration-300 flex items-center justify-center text-[9px] font-bold text-gray-950"
            >
              {restMinutes > 10 ? `${restMinutes}m` : ''}
            </div>
          </div>
        </div>

        {/* Hydration & Safety Alerts */}
        <div className="bg-gray-950 p-3 rounded-lg border border-gray-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400 flex items-center gap-1">
              💧 Mandatory Hydration:
            </span>
            <strong className="text-cyan-400">{hydrationMl} ml / hour</strong>
          </div>

          {warnings.length > 0 && (
            <div className="pt-2 border-t border-gray-800/80 text-[11px] text-amber-300/90 leading-tight">
              ⚠️ {warnings[0]}
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <p className="text-[10px] text-gray-500 italic text-center">
          Operational Decision Support (aligned with ACGIH/NIOSH thresholds).
        </p>
      </div>
    </div>
  );
}
