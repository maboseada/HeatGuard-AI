import React from 'react';
import MetricCard from './MetricCard';
import { DataProvenance } from '@/types';

interface Props {
  value: number | null;
  provenance?: DataProvenance;
}

export default function HeatIndexCard({ value, provenance }: Props) {
  return (
    <MetricCard
      title="Heat Index"
      value={value}
      unit="°C"
      colorClass="bg-amber-500"
      provenance={provenance}
      icon={
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
        </svg>
      }
    />
  );
}
