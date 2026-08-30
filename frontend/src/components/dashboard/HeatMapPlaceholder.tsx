import React from 'react';

export default function HeatMapPlaceholder() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden flex flex-col h-full min-h-[350px] relative">
      <div className="p-4 border-b border-gray-800 bg-gray-900 z-10 flex justify-between items-center">
        <h3 className="text-sm font-semibold text-gray-200">Site Heatmap Visualization</h3>
        <span className="text-xs font-medium text-amber-500 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20">Phase 2</span>
      </div>
      
      {/* Prepared div for future map injection */}
      <div id="heatmap-container" className="flex-1 bg-gray-950 relative flex items-center justify-center p-6 text-center">
        {/* Placeholder grid background effect */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
        
        <div className="relative z-10 max-w-sm">
          <div className="w-16 h-16 bg-gray-800 border border-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <h4 className="text-lg font-medium text-gray-300 mb-2">Map Integration Coming Soon</h4>
          <p className="text-sm text-gray-500">
            Phase 2 will introduce interactive Leaflet/Mapbox integration with live FortyGuard heatmap overlays for hyper-local microclimate monitoring.
          </p>
        </div>
      </div>
    </div>
  );
}
