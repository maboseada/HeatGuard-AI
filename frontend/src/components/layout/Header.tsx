"use client";
import { useEffect, useState } from 'react';
import { checkHealth } from '@/lib/api';
import { AssessmentMode } from '@/types';

interface HeaderProps {
  mode: AssessmentMode;
  onModeChange: (mode: AssessmentMode) => void;
  onOpenReport?: () => void;
}

export default function Header({ mode, onModeChange, onOpenReport }: HeaderProps) {
  const [isApiHealthy, setIsApiHealthy] = useState<boolean>(false);

  useEffect(() => {
    checkHealth().then(setIsApiHealthy).catch(() => setIsApiHealthy(false));
  }, []);

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex flex-wrap items-center justify-between sticky top-0 z-10 shadow-sm gap-3">
      <div>
        <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2">
          <span>HeatGuard AI</span>
          <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            HSE PLATFORM
          </span>
        </h2>
        <p className="text-xs text-gray-400">Microclimate thermal risk & HSE decision support</p>
      </div>
      
      <div className="flex items-center gap-3">
        {/* Mode Selector Toggle */}
        <div className="flex items-center bg-gray-950 p-1 rounded-lg border border-gray-800 text-xs">
          <button
            onClick={() => onModeChange('DEMO')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              mode === 'DEMO'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            🟡 DEMO (SYNTHETIC)
          </button>
          <button
            onClick={() => onModeChange('LIVE')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              mode === 'LIVE'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            🟢 LIVE FORTYGUARD
          </button>
        </div>

        {/* 1-Click Export HSE Briefing */}
        <button
          onClick={onOpenReport}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-200 text-xs font-semibold shadow-sm transition-all hover:border-gray-600 active:scale-95"
        >
          <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export HSE Plan
        </button>

        {/* Backend Connectivity Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-800 border border-gray-700">
          <div className={`w-2 h-2 rounded-full ${isApiHealthy ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' : 'bg-rose-500'}`}></div>
          <span className="text-xs font-medium text-gray-300">
            {isApiHealthy ? 'Online' : 'Connecting...'}
          </span>
        </div>
      </div>
    </header>
  );
}
