"use client";
import React, { useState, useEffect } from 'react';
import { runWhatIfSimulation } from '@/lib/api';
import { WhatIfSimulationResult, WorkloadCategory } from '@/types';

interface Props {
  baselineTemperature: number;
  baselineWetBulb: number;
  baselineSolarGhi: number;
  workload: WorkloadCategory;
}

export default function WhatIfSimulator({
  baselineTemperature,
  baselineWetBulb,
  baselineSolarGhi,
  workload,
}: Props) {
  const [shadePercent, setShadePercent] = useState<number>(50);
  const [mistingPercent, setMistingPercent] = useState<number>(40);
  const [simulation, setSimulation] = useState<WhatIfSimulationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setIsSimulating(true);

    const debounceTimer = setTimeout(() => {
      runWhatIfSimulation(
        baselineTemperature,
        baselineWetBulb,
        baselineSolarGhi,
        shadePercent,
        mistingPercent,
        workload
      )
        .then((res) => {
          if (isMounted) setSimulation(res);
        })
        .catch((e) => console.error("Simulation error:", e))
        .finally(() => {
          if (isMounted) setIsSimulating(false);
        });
    }, 150);

    return () => {
      isMounted = false;
      clearTimeout(debounceTimer);
    };
  }, [baselineTemperature, baselineWetBulb, baselineSolarGhi, shadePercent, mistingPercent, workload]);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden shadow-xl">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 bg-gray-900 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-100">What-If Safety Mitigation Simulator</h3>
        </div>
        <span className="text-[9px] font-bold tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/30">
          ESTIMATED SIMULATION
        </span>
      </div>

      <div className="p-5 space-y-6">
        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-gray-950 p-4 rounded-lg border border-gray-800">
          {/* Shading Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-semibold text-gray-300">⛱️ Temporary Shading Canopy:</span>
              <strong className="text-amber-400">{shadePercent}% coverage</strong>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={shadePercent}
              onChange={(e) => setShadePercent(Number(e.target.value))}
              className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <span className="text-[10px] text-gray-500 block">Attenuates direct solar radiant heat load</span>
          </div>

          {/* Misting Slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-semibold text-gray-300">💨 High-Pressure Misting Fans:</span>
              <strong className="text-cyan-400">{mistingPercent}% capacity</strong>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={mistingPercent}
              onChange={(e) => setMistingPercent(Number(e.target.value))}
              className="w-full h-2 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <span className="text-[10px] text-gray-500 block">Provides localized evaporative depression cooling</span>
          </div>
        </div>

        {/* Side-by-Side Comparison Grid */}
        {simulation && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              {/* Solar Comparison */}
              <div className="bg-gray-950 p-3 rounded-lg border border-gray-800">
                <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Solar Irradiance</span>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-gray-400 line-through text-[11px]">{simulation.effective_solar_irradiance.baseline.toFixed(0)}</span>
                  <span className="text-base font-bold text-amber-400">{simulation.effective_solar_irradiance.simulated.toFixed(0)}</span>
                  <span className="text-[10px] text-gray-500">W/m²</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-semibold">{simulation.effective_solar_irradiance.delta} W/m²</span>
              </div>

              {/* Effective Temp Comparison */}
              <div className="bg-gray-950 p-3 rounded-lg border border-gray-800">
                <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Effective Temp</span>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-gray-400 line-through text-[11px]">{simulation.effective_temperature.baseline.toFixed(1)}°C</span>
                  <span className="text-base font-bold text-rose-400">{simulation.effective_temperature.simulated.toFixed(1)}°C</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-semibold">{simulation.effective_temperature.delta}°C relief</span>
              </div>

              {/* Estimated WBGT Comparison */}
              <div className="bg-gray-950 p-3 rounded-lg border border-gray-800">
                <span className="text-[10px] text-gray-400 uppercase font-bold block mb-1">Estimated WBGT</span>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-gray-400 line-through text-[11px]">{simulation.estimated_wbgt.baseline.toFixed(1)}°C</span>
                  <span className="text-base font-bold text-teal-400">{simulation.estimated_wbgt.simulated.toFixed(1)}°C</span>
                </div>
                <span className="text-[10px] text-emerald-400 font-semibold">{simulation.estimated_wbgt.delta}°C strain</span>
              </div>

              {/* Recovered Productivity */}
              <div className="bg-emerald-950/40 p-3 rounded-lg border border-emerald-500/30">
                <span className="text-[10px] text-emerald-300 uppercase font-bold block mb-1">Recovered Labor</span>
                <div className="text-xl font-black text-emerald-400">
                  +{simulation.recovered_work_minutes_per_hour} <span className="text-xs font-normal text-emerald-300">min/hr</span>
                </div>
                <span className="text-[10px] text-emerald-300/80">Regained shift capacity</span>
              </div>
            </div>

            {/* Protocol Shift Comparison */}
            <div className="bg-gray-950 p-3 rounded-lg border border-gray-800 flex flex-col sm:flex-row justify-between items-center gap-3 text-xs">
              <div>
                <span className="text-gray-400">Baseline Schedule:</span>{' '}
                <strong className="text-rose-400">{simulation.baseline_protocol.work_rest_ratio}</strong>
              </div>
              <div className="text-gray-500">──►</div>
              <div>
                <span className="text-gray-400">Simulated Schedule:</span>{' '}
                <strong className="text-emerald-400">{simulation.simulated_protocol.work_rest_ratio}</strong>
              </div>
            </div>
          </div>
        )}

        {/* Assumptions List */}
        <div className="text-[10px] text-gray-500 border-t border-gray-800/80 pt-2 space-y-0.5">
          <span className="font-semibold text-gray-400">Explicit Modeling Assumptions:</span>
          <p>• Max 85% solar attenuation under 100% shade coverage.</p>
          <p>• Max 35% wet-bulb depression cooling under high-pressure misting airflow.</p>
        </div>
      </div>
    </div>
  );
}
