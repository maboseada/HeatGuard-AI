import React from 'react';
import MetricCard from './MetricCard';
import { DataProvenance } from '@/types';

interface Props {
  value: number | null;
  provenance?: DataProvenance;
}

export default function HumidityCard({ value, provenance }: Props) {
  return (
    <MetricCard
      title="Relative Humidity"
      value={value}
      unit="%"
      colorClass="bg-blue-500"
      provenance={provenance}
      icon={
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 00-9.78 2.096A4.001 4.001 0 003 15z" />
        </svg>
      }
    />
  );
}
