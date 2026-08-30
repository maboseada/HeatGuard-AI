"use client";
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { DataProvenance } from '@/types';

// Dynamic import with SSR disabled to prevent Leaflet window errors
const ThermalMapInner = dynamic(() => import('./ThermalMapInner'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[420px] bg-gray-950 flex flex-col items-center justify-center text-gray-500 gap-3">
      <div className="w-8 h-8 border-2 border-amber-500/20 border-t-amber-500 rounded-full animate-spin"></div>
      <span className="text-xs">Initializing High-Resolution Thermal Canvas...</span>
    </div>
  )
});

interface Props {
  center?: [number, number];
  zoom?: number;
  geoJsonData?: any | null;
  provenance?: DataProvenance;
  onCellSelect?: (cellId: string | null) => void;
}

export default function ThermalMap({
  center = [25.2048, 55.2708],
  zoom = 15,
  geoJsonData = null,
  provenance = 'demo_synthetic',
  onCellSelect
}: Props) {
  const [inspectedCell, setInspectedCell] = useState<any | null>(null);

  const handleCellClick = (cellProps: any) => {
    setInspectedCell(cellProps);
    if (cellProps?.cell_id) {
      onCellSelect?.(cellProps.cell_id);
    }
  };

  const getProvenanceBadge = () => {
    switch (provenance) {
      case 'raw_fortyguard':
        return (
          <span className="text-[9px] font-bold tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
            LIVE FORTYGUARD GEOJSON
          </span>
        );
      case 'demo_synthetic':
      default:
        return (
          <span className="text-[9px] font-bold tracking-wider text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
            SYNTHETIC BENCHMARK GRID
          </span>
        );
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden flex flex-col h-full min-h-[480px] relative shadow-md">
      {/* Header bar */}
      <div className="p-4 border-b border-gray-800 bg-gray-900 z-10 flex flex-wrap justify-between items-center gap-2">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-100">Hyperlocal Thermal Surface Analysis</h3>
        </div>
        
        {getProvenanceBadge()}
      </div>

      {/* Map Body */}
      <div className="flex-1 relative">
        <ThermalMapInner
          center={center}
          zoom={zoom}
          geoJsonData={geoJsonData}
          onCellClick={handleCellClick}
        />

        {/* Selected Cell Detail Drawer */}
        {inspectedCell && (
          <div className="absolute top-3 left-3 z-[1000] bg-gray-950/95 backdrop-blur-md border border-gray-700 p-3.5 rounded-lg max-w-xs shadow-2xl animate-in fade-in slide-in-from-top duration-200">
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-xs font-bold text-gray-200">{inspectedCell.zone_name || `Grid Cell ${inspectedCell.cell_id}`}</h4>
              <button
                onClick={() => {
                  setInspectedCell(null);
                  onCellSelect?.(null);
                }}
                className="text-gray-500 hover:text-gray-300 text-xs px-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-1.5 text-[11px]">
              <div className="flex justify-between">
                <span className="text-gray-400">Micro-Surface Temp:</span>
                <span className="font-bold text-amber-400">{inspectedCell.temperature?.toFixed(1)}°C</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Thermal Exceedance:</span>
                <span className="font-semibold text-gray-200">+{inspectedCell.exceedance?.toFixed(1)}°C</span>
              </div>
              {inspectedCell.is_hotspot && (
                <div className="mt-2 pt-2 border-t border-gray-800 text-[10px] text-rose-400 font-semibold flex items-center gap-1">
                  <span>🔥 Critical Hotspot Focus</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
