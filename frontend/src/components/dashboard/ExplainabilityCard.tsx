"use client";
import React from 'react';
import { ExplainabilityReport } from '@/types';

interface Props {
  report: ExplainabilityReport | null;
  isLoading?: boolean;
}

export default function ExplainabilityCard({ report, isLoading = false }: Props) {
  if (isLoading) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 animate-pulse">
        <div className="h-4 bg-gray-800 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-gray-950 rounded border border-gray-800"></div>
          <div className="h-24 bg-gray-950 rounded border border-gray-800"></div>
          <div className="h-20 bg-gray-950 rounded border border-gray-800"></div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 flex flex-col items-center justify-center text-center min-h-[300px]">
        <div className="w-12 h-12 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-gray-500 mb-3">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h4 className="text-sm font-medium text-gray-300">Awaiting Site Selection & Assessment</h4>
        <p className="text-xs text-gray-500 max-w-xs mt-1">
          Select an industrial facility or click a specific map hotspot cell to view the transparent WHERE / WHY / WHAT explainability diagnostic.
        </p>
      </div>
    );
  }

  const { where, why, what } = report;

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'Critical':
        return <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/30">CRITICAL DRIVER</span>;
      case 'High':
        return <span className="text-[10px] font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/30">HIGH LOAD</span>;
      case 'Moderate':
        return <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">MODERATE</span>;
      default:
        return <span className="text-[10px] font-medium text-gray-400 bg-gray-800 px-2 py-0.5 rounded">NORMAL</span>;
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden shadow-lg">
      {/* Card Header */}
      <div className="p-4 border-b border-gray-800 bg-gray-900 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-100">Explainability Diagnostic (WHERE / WHY / WHAT)</h3>
        </div>
        <span className="text-[9px] font-bold tracking-wider text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
          DERIVED AUDIT
        </span>
      </div>

      <div className="p-5 space-y-5">
        {/* 1. WHERE */}
        <div className="bg-gray-950/80 border border-gray-800/80 rounded-lg p-3.5">
          <div className="text-[11px] font-bold tracking-wider uppercase text-amber-400 mb-1.5 flex items-center justify-between">
            <span>1. WHERE IS THE RISK?</span>
            <span className="text-gray-500 font-mono text-[10px]">
              [{where.coordinates[0].toFixed(4)}, {where.coordinates[1].toFixed(4)}]
            </span>
          </div>
          <div className="text-xs text-gray-300 font-medium">
            <span className="text-gray-100 font-semibold">{where.zone_label}</span> ({where.grid_cell_id})
          </div>
          <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
            <div>Surface Temp: <strong className="text-amber-400">{where.micro_surface_temperature?.toFixed(1)}°C</strong></div>
            {where.thermal_exceedance_delta !== null && (
              <div>Exceedance vs Ambient: <strong className="text-rose-400">+{where.thermal_exceedance_delta.toFixed(1)}°C</strong></div>
            )}
          </div>
        </div>

        {/* 2. WHY */}
        <div className="bg-gray-950/80 border border-gray-800/80 rounded-lg p-3.5">
          <div className="text-[11px] font-bold tracking-wider uppercase text-amber-400 mb-2">
            2. WHY IS IT HAPPENING? (FACTOR DECOMPOSITION)
          </div>
          <p className="text-xs text-gray-300 mb-3 italic">
            &ldquo;{why.primary_risk_driver}&rdquo;
          </p>
          <div className="space-y-2">
            {why.factor_contributions.map((fc, idx) => (
              <div key={idx} className="flex items-center justify-between bg-gray-900 border border-gray-800/60 p-2 rounded text-xs">
                <div>
                  <div className="font-semibold text-gray-200">{fc.factor} <span className="text-amber-400 ml-1">({fc.raw_value})</span></div>
                  <div className="text-[11px] text-gray-400 mt-0.5">{fc.explanation}</div>
                </div>
                <div>{getLevelBadge(fc.contribution_level)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. WHAT */}
        <div className="bg-gray-950/80 border border-gray-800/80 rounded-lg p-3.5">
          <div className="text-[11px] font-bold tracking-wider uppercase text-emerald-400 mb-2">
            3. WHAT SHOULD THE OPERATOR DO? (PRESCRIPTIVE ACTION)
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="bg-gray-900 p-2.5 rounded border border-gray-800">
              <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Work-Rest Protocol</span>
              <strong className="text-emerald-300 text-sm">{what.work_rest_guidance}</strong>
            </div>
            <div className="bg-gray-900 p-2.5 rounded border border-gray-800">
              <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Hydration Target</span>
              <strong className="text-cyan-300 text-sm">{what.hydration_guidance}</strong>
            </div>
          </div>

          {what.critical_ppe_actions.length > 0 && (
            <div className="mt-3 text-xs text-gray-300">
              <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">PPE Modifications:</span>
              <ul className="list-disc list-inside space-y-0.5 text-gray-300">
                {what.critical_ppe_actions.map((act, idx) => (
                  <li key={idx}>{act}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
