"use client";
import { useEffect, useState } from 'react';
import { Site } from '@/types';
import { fetchSites } from '@/lib/api';
import { MOCK_SITES } from '@/lib/mockData';

interface SiteSelectorProps {
  onSelect?: (site: Site) => void;
  onRunAssessment?: () => void;
  isAssessing?: boolean;
}

export default function SiteSelector({
  onSelect,
  onRunAssessment,
  isAssessing = false
}: SiteSelectorProps) {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string>('');
  
  useEffect(() => {
    fetchSites()
      .then(data => {
        if (data && data.length > 0) {
          setSites(data);
          setSelectedId(data[0].id);
          onSelect?.(data[0]);
        } else {
          setSites(MOCK_SITES);
          setSelectedId(MOCK_SITES[0].id);
          onSelect?.(MOCK_SITES[0]);
        }
      })
      .catch(() => {
        setSites(MOCK_SITES);
        setSelectedId(MOCK_SITES[0].id);
        onSelect?.(MOCK_SITES[0]);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    setSelectedId(id);
    const site = sites.find(s => s.id === id);
    if (site) onSelect?.(site);
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-100 flex items-center gap-2">
          <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Industrial Facility Selection
        </h2>
        <p className="text-xs text-gray-400">Select operational boundary for microclimate analysis</p>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="relative min-w-[240px]">
          {loading ? (
            <div className="h-10 bg-gray-800 animate-pulse rounded border border-gray-700 w-full"></div>
          ) : (
            <select 
              value={selectedId}
              onChange={handleChange}
              className="w-full bg-gray-950 border border-gray-700 text-gray-200 text-sm rounded-lg focus:ring-amber-500 focus:border-amber-500 block p-2.5 outline-none appearance-none cursor-pointer"
            >
              {sites.map(site => (
                <option key={site.id} value={site.id}>{site.name}</option>
              ))}
            </select>
          )}
          {!loading && (
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          )}
        </div>

        <button
          onClick={onRunAssessment}
          disabled={isAssessing}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all ${
            isAssessing
              ? 'bg-amber-600/50 text-amber-200 cursor-not-allowed animate-pulse'
              : 'bg-amber-500 hover:bg-amber-400 text-gray-950 shadow-md hover:shadow-amber-500/20 active:scale-95'
          }`}
        >
          {isAssessing ? (
            <>
              <svg className="animate-spin -ml-1 mr-1 h-4 w-4 text-gray-950" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Assessing Zone...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run Site Assessment
            </>
          )}
        </button>
      </div>
    </div>
  );
}
