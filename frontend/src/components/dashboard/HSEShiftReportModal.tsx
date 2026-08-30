"use client";
import React from 'react';
import { ExplainabilityReport, Site, AssessmentResponse } from '@/types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  site: Site | null;
  assessment: AssessmentResponse | null;
  report: ExplainabilityReport | null;
}

export default function HSEShiftReportModal({
  isOpen,
  onClose,
  site,
  assessment,
  report
}: Props) {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const env = assessment?.environmental;
  const stats = assessment?.stats;
  const isLive = assessment?.mode === 'LIVE';

  return (
    <div className="fixed inset-0 z-[9999] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      {/* Container */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        {/* Modal Toolbar (hidden during print) */}
        <div className="p-4 border-b border-gray-800 bg-gray-950 flex justify-between items-center print:hidden sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <h3 className="text-sm font-bold text-gray-100">Official HSE Shift Safety Briefing Plan</h3>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 text-xs font-bold shadow-md transition-all active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Print / Save as PDF
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-200 text-sm px-2 py-1"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Printable Report Document */}
        <div id="printable-hse-report" className="p-8 space-y-6 text-gray-200 bg-gray-900 print:bg-white print:text-black print:p-4">
          {/* Header Title */}
          <div className="border-b-2 border-amber-500 pb-4 flex justify-between items-start">
            <div>
              <div className="text-xs font-mono uppercase tracking-widest text-amber-500 font-bold">
                HEATGUARD AI — INDUSTRIAL RISK INTELLIGENCE
              </div>
              <h1 className="text-2xl font-black text-gray-100 print:text-black mt-1">
                HSE Operational Heat Stress Briefing
              </h1>
              <p className="text-xs text-gray-400 print:text-gray-600 mt-0.5">
                Facility: <strong className="text-gray-200 print:text-black">{site?.name || 'Industrial Facility'}</strong>
              </p>
            </div>

            <div className="text-right text-xs">
              <div className="text-gray-400 print:text-gray-600">Generated: {currentDate}</div>
              <div className="mt-1">
                {isLive ? (
                  <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30 print:border-black print:text-black">
                    SOURCE: LIVE FORTYGUARD STREAM
                  </span>
                ) : (
                  <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30 print:border-black print:text-black">
                    SOURCE: SYNTHETIC BENCHMARK
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Key Facility Microclimate Parameters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="bg-gray-950 p-3 rounded border border-gray-800 print:border-gray-300 print:bg-gray-50">
              <span className="text-gray-400 print:text-gray-600 block text-[10px] uppercase font-bold">Ambient Dry Bulb</span>
              <strong className="text-base text-gray-100 print:text-black">{env?.temperature?.toFixed(1) || '38.5'}°C</strong>
            </div>
            <div className="bg-gray-950 p-3 rounded border border-gray-800 print:border-gray-300 print:bg-gray-50">
              <span className="text-gray-400 print:text-gray-600 block text-[10px] uppercase font-bold">Wet Bulb Temp</span>
              <strong className="text-base text-teal-400 print:text-black">{env?.wet_bulb_temperature?.toFixed(1) || '28.5'}°C</strong>
            </div>
            <div className="bg-gray-950 p-3 rounded border border-gray-800 print:border-gray-300 print:bg-gray-50">
              <span className="text-gray-400 print:text-gray-600 block text-[10px] uppercase font-bold">Estimated WBGT</span>
              <strong className="text-base text-amber-400 print:text-black">{report?.what.estimated_wbgt?.toFixed(1) || '32.4'}°C</strong>
            </div>
            <div className="bg-gray-950 p-3 rounded border border-gray-800 print:border-gray-300 print:bg-gray-50">
              <span className="text-gray-400 print:text-gray-600 block text-[10px] uppercase font-bold">Max Hotspot Exceedance</span>
              <strong className="text-base text-rose-400 print:text-black">
                {stats?.max_temperature ? `${stats.max_temperature.toFixed(1)}°C` : '44.2°C'}
              </strong>
            </div>
          </div>

          {/* Work-Rest Protocol Matrix */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 print:text-black">
              1. Prescribed Work-to-Rest Shift Schedule
            </h3>
            <table className="w-full text-xs text-left border-collapse border border-gray-800 print:border-gray-400">
              <thead className="bg-gray-950 text-gray-300 print:bg-gray-100 print:text-black">
                <tr>
                  <th className="border border-gray-800 print:border-gray-400 p-2">Labor Workload Category</th>
                  <th className="border border-gray-800 print:border-gray-400 p-2">Cycle Ratio (Work / Rest)</th>
                  <th className="border border-gray-800 print:border-gray-400 p-2">Mandatory Hydration Quota</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 print:divide-gray-400 text-gray-300 print:text-black">
                <tr>
                  <td className="border border-gray-800 print:border-gray-400 p-2 font-medium">Light Labor (Inspection / Driving)</td>
                  <td className="border border-gray-800 print:border-gray-400 p-2 text-emerald-400 print:text-black font-semibold">45 min Work / 15 min Rest</td>
                  <td className="border border-gray-800 print:border-gray-400 p-2">500 ml / hour</td>
                </tr>
                <tr className="bg-gray-950/50 print:bg-gray-50">
                  <td className="border border-gray-800 print:border-gray-400 p-2 font-medium">Moderate Labor (Assembly / Pipefitting)</td>
                  <td className="border border-gray-800 print:border-gray-400 p-2 text-amber-400 print:text-black font-bold">30 min Work / 30 min Rest</td>
                  <td className="border border-gray-800 print:border-gray-400 p-2">750 ml / hour</td>
                </tr>
                <tr>
                  <td className="border border-gray-800 print:border-gray-400 p-2 font-medium">Heavy Labor (Scaffolding / Lifting)</td>
                  <td className="border border-gray-800 print:border-gray-400 p-2 text-rose-400 print:text-black font-bold">15 min Work / 45 min Rest</td>
                  <td className="border border-gray-800 print:border-gray-400 p-2">1,000 ml / hour</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Mandatory Safety PPE & Engineering Controls */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="bg-gray-950 p-4 rounded border border-gray-800 print:border-gray-300 print:bg-transparent">
              <h4 className="font-bold text-gray-200 print:text-black uppercase text-[11px] mb-2">
                2. Mandatory PPE Modifications
              </h4>
              <ul className="list-disc list-inside space-y-1 text-gray-300 print:text-black text-[11px]">
                <li>Hard hat UV shade neck flaps mandatory on open yards.</li>
                <li>Prohibit impermeable vapor-barrier suits without cooling vests.</li>
                <li>Provide polarized UV400 safety eyewear for high reflection sectors.</li>
              </ul>
            </div>

            <div className="bg-gray-950 p-4 rounded border border-gray-800 print:border-gray-300 print:bg-transparent">
              <h4 className="font-bold text-gray-200 print:text-black uppercase text-[11px] mb-2">
                3. Site Engineering Controls
              </h4>
              <ul className="list-disc list-inside space-y-1 text-gray-300 print:text-black text-[11px]">
                <li>Deploy temporary shade canopies at Sector Hotspot Centroid.</li>
                <li>Activate high-pressure misting stations at designated rest tents.</li>
                <li>Stage cold electrolyte hydration replenishment points within 50m of work zones.</li>
              </ul>
            </div>
          </div>

          {/* Sign-off Block */}
          <div className="pt-6 border-t border-gray-800 print:border-gray-400 grid grid-cols-2 gap-8 text-xs text-gray-400 print:text-black">
            <div>
              <div className="font-semibold text-gray-300 print:text-black">HSE Safety Officer Name:</div>
              <div className="border-b border-gray-700 print:border-black mt-6 w-4/5"></div>
            </div>
            <div>
              <div className="font-semibold text-gray-300 print:text-black">Supervisor Authorization Signature:</div>
              <div className="border-b border-gray-700 print:border-black mt-6 w-4/5"></div>
            </div>
          </div>

          <div className="text-[10px] text-gray-500 text-center italic">
            HeatGuard AI Operational Safety Matrix • Powered by FortyGuard Microclimate Intelligence
          </div>
        </div>
      </div>
    </div>
  );
}
