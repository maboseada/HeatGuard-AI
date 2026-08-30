"use client";
import React, { useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';

interface Props {
  center: [number, number];
  zoom: number;
  geoJsonData: any | null;
  onCellClick?: (properties: any) => void;
}

// Helper to auto-fit map bounds when GeoJSON changes
function MapBoundsUpdater({ geoJsonData, center }: { geoJsonData: any; center: [number, number] }) {
  const map = useMap();

  React.useEffect(() => {
    if (geoJsonData && geoJsonData.features && geoJsonData.features.length > 0) {
      try {
        const layer = L.geoJSON(geoJsonData);
        map.fitBounds(layer.getBounds(), { padding: [30, 30] });
      } catch (e) {
        map.setView(center, 15);
      }
    } else {
      map.setView(center, 15);
    }
  }, [geoJsonData, center, map]);

  return null;
}

export default function ThermalMapInner({ center, zoom, geoJsonData, onCellClick }: Props) {
  const [tileType, setTileType] = useState<'dark' | 'satellite'>('dark');

  // Thermal color gradient based on surface temperature in °C
  const getCellColor = (temp: number) => {
    if (temp >= 43) return '#ef4444'; // Red (Extreme)
    if (temp >= 40) return '#f97316'; // Orange (High)
    if (temp >= 37) return '#f59e0b'; // Amber (Moderate)
    return '#10b981';                 // Green (Normal)
  };

  const styleGeoJson = (feature: any) => {
    const temp = feature?.properties?.temperature || 36.0;
    const isHotspot = feature?.properties?.is_hotspot || false;

    return {
      fillColor: getCellColor(temp),
      weight: isHotspot ? 2.5 : 1,
      opacity: 1,
      color: isHotspot ? '#ffffff' : '#4b5563',
      fillOpacity: 0.65,
    };
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    const props = feature.properties || {};
    const temp = props.temperature ? `${props.temperature.toFixed(1)}°C` : 'N/A';
    const exceedance = props.exceedance ? `+${props.exceedance.toFixed(1)}°C` : '0°C';
    const zoneName = props.zone_name || `Cell ${props.cell_id || ''}`;
    const hotspotBadge = props.is_hotspot ? '<span style="color:#ef4444;font-weight:bold;">🔥 CRITICAL HOTSPOT</span><br/>' : '';

    layer.bindPopup(`
      <div style="font-family: inherit; font-size: 12px; line-height: 1.5;">
        <strong style="color: #f3f4f6; font-size: 13px;">${zoneName}</strong><br/>
        ${hotspotBadge}
        <span style="color: #9ca3af;">Surface Temp:</span> <strong style="color: #f59e0b;">${temp}</strong><br/>
        <span style="color: #9ca3af;">Thermal Exceedance:</span> <strong>${exceedance}</strong>
      </div>
    `);

    layer.on({
      click: () => {
        onCellClick?.(props);
      },
      mouseover: (e) => {
        const target = e.target;
        target.setStyle({
          fillOpacity: 0.85,
          weight: 2,
          color: '#ffffff'
        });
      },
      mouseout: (e) => {
        const target = e.target;
        target.setStyle(styleGeoJson(feature));
      }
    });
  };

  return (
    <div className="relative w-full h-full min-h-[420px] rounded-b-lg overflow-hidden">
      {/* Base Layer Switcher */}
      <div className="absolute top-3 right-3 z-[1000] bg-gray-900/90 backdrop-blur-sm border border-gray-800 p-1 rounded-lg flex gap-1 text-[11px] shadow-lg">
        <button
          onClick={() => setTileType('dark')}
          className={`px-2.5 py-1 rounded font-medium transition-all ${
            tileType === 'dark' ? 'bg-gray-800 text-amber-400 border border-gray-700' : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Dark Canvas
        </button>
        <button
          onClick={() => setTileType('satellite')}
          className={`px-2.5 py-1 rounded font-medium transition-all ${
            tileType === 'satellite' ? 'bg-gray-800 text-amber-400 border border-gray-700' : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Satellite
        </button>
      </div>

      {/* Map Canvas */}
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%', minHeight: '420px' }}
        zoomControl={false}
      >
        {tileType === 'dark' ? (
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
        ) : (
          <TileLayer
            attribution='&copy; Esri World Imagery'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        )}

        {geoJsonData && (
          <GeoJSON
            key={JSON.stringify(geoJsonData)}
            data={geoJsonData}
            style={styleGeoJson}
            onEachFeature={onEachFeature}
          />
        )}

        <MapBoundsUpdater geoJsonData={geoJsonData} center={center} />
      </MapContainer>

      {/* Thermal Gradient Legend */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-gray-950/90 backdrop-blur-md border border-gray-800 px-3 py-2 rounded-lg text-xs shadow-xl">
        <div className="text-[10px] uppercase font-bold tracking-wider text-gray-400 mb-1.5 flex items-center justify-between gap-4">
          <span>FortyGuard Thermal Scale</span>
          <span className="text-gray-500 font-mono text-[9px]">60m Cells</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-sm bg-emerald-500"></span>
            <span className="text-[10px] text-gray-300">&lt;37°C</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-sm bg-amber-500"></span>
            <span className="text-[10px] text-gray-300">37-40°C</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-sm bg-orange-500"></span>
            <span className="text-[10px] text-gray-300">40-43°C</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-sm bg-rose-500 animate-pulse"></span>
            <span className="text-[10px] text-rose-400 font-semibold">&gt;43°C Hotspot</span>
          </div>
        </div>
      </div>
    </div>
  );
}
