"use client";
import { useState, useEffect } from "react";
import SiteSelector from "@/components/dashboard/SiteSelector";
import RiskCard from "@/components/dashboard/RiskCard";
import TemperatureCard from "@/components/dashboard/TemperatureCard";
import HeatIndexCard from "@/components/dashboard/HeatIndexCard";
import WetBulbCard from "@/components/dashboard/WetBulbCard";
import HumidityCard from "@/components/dashboard/HumidityCard";
import ThermalMap from "@/components/dashboard/map/ThermalMap";
import ExplainabilityCard from "@/components/dashboard/ExplainabilityCard";
import HSEProtocolCard from "@/components/dashboard/HSEProtocolCard";
import WhatIfSimulator from "@/components/dashboard/WhatIfSimulator";
import HSEShiftReportModal from "@/components/dashboard/HSEShiftReportModal";
import Header from "@/components/layout/Header";
import {
  Site,
  AssessmentResponse,
  AssessmentMode,
  DataProvenance,
  WorkloadCategory,
  ExplainabilityReport,
} from "@/types";
import {
  triggerAssessment,
  fetchAssessment,
  fetchLatestAssessment,
  fetchExplainabilityReport,
} from "@/lib/api";
import { MOCK_ENVIRONMENTAL } from "@/lib/mockData";

export default function DashboardPage() {
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const [mode, setMode] = useState<AssessmentMode>('DEMO');
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [isAssessing, setIsAssessing] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);

  // Phase 3 Intelligence State
  const [workload, setWorkload] = useState<WorkloadCategory>('Moderate');
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null);
  const [explainReport, setExplainReport] = useState<ExplainabilityReport | null>(null);
  const [loadingExplain, setLoadingExplain] = useState<boolean>(false);

  // Load existing assessment when site changes
  useEffect(() => {
    if (selectedSite) {
      setSelectedCellId(null);
      fetchLatestAssessment(selectedSite.id)
        .then((data) => {
          if (data) setAssessment(data);
        })
        .catch(() => {});
    }
  }, [selectedSite]);

  // Fetch / Refresh Explainability Report when site, assessment, cell, or workload changes
  useEffect(() => {
    if (selectedSite) {
      setLoadingExplain(true);
      fetchExplainabilityReport(selectedSite.id, selectedCellId, workload)
        .then((rep) => setExplainReport(rep))
        .catch((err) => console.error("Failed to load explainability:", err))
        .finally(() => setLoadingExplain(false));
    }
  }, [selectedSite, assessment, selectedCellId, workload]);

  const handleRunAssessment = async () => {
    if (!selectedSite || isAssessing) return;

    setIsAssessing(true);
    setStatusMessage(
      mode === 'LIVE'
        ? "Submitting tasks to FortyGuard API (60m resolution)..."
        : "Executing instant synthetic benchmark assessment..."
    );

    try {
      const initial = await triggerAssessment(selectedSite.id, mode, 60);
      setAssessment(initial);

      if (initial.status === 'Completed') {
        setIsAssessing(false);
        setStatusMessage("Assessment complete.");
        setTimeout(() => setStatusMessage(null), 3000);
        return;
      }

      // If in LIVE mode and processing, poll status
      const pollInterval = setInterval(async () => {
        try {
          const updated = await fetchAssessment(initial.id);
          setAssessment(updated);

          if (updated.status === 'Completed') {
            clearInterval(pollInterval);
            setIsAssessing(false);
            setStatusMessage("FortyGuard analysis complete and normalized.");
            setTimeout(() => setStatusMessage(null), 4000);
          } else if (updated.status === 'Failed') {
            clearInterval(pollInterval);
            setIsAssessing(false);
            setStatusMessage(`Assessment failed: ${updated.error_message || 'Unknown error'}`);
          }
        } catch (e) {
          console.error("Polling error:", e);
        }
      }, 3000);
    } catch (err: any) {
      console.error("Assessment trigger failed:", err);
      setIsAssessing(false);
      setStatusMessage("Failed to initiate assessment.");
      setTimeout(() => setStatusMessage(null), 4000);
    }
  };

  // Extract environmental metrics or fall back to mock
  const currentEnv = assessment?.environmental || {
    provenance: 'demo_synthetic' as DataProvenance,
    temperature: MOCK_ENVIRONMENTAL.temperature,
    heat_index: MOCK_ENVIRONMENTAL.heat_index,
    apparent_temperature: MOCK_ENVIRONMENTAL.apparent_temperature,
    wet_bulb_temperature: MOCK_ENVIRONMENTAL.wet_bulb_temperature,
    relative_humidity: MOCK_ENVIRONMENTAL.relative_humidity,
    solar_irradiance: MOCK_ENVIRONMENTAL.solar_ghi,
    precipitation_mm: 0,
    cloud_cover_octas: 0,
    air_quality_index: null,
  };

  const currentProvenance: DataProvenance = currentEnv.provenance;

  // Use explain report derived values or fallback
  const riskCategory = (explainReport?.what.risk_category as 'Low' | 'Moderate' | 'High' | 'Extreme') || 'Moderate';

  // Map center coordinates
  const mapCenter: [number, number] = selectedSite
    ? [selectedSite.latitude, selectedSite.longitude]
    : [25.2048, 55.2708];

  return (
    <div className="space-y-6 pb-16">
      {/* Top Header with Mode Switcher & Report Trigger */}
      <Header
        mode={mode}
        onModeChange={setMode}
        onOpenReport={() => setIsReportOpen(true)}
      />

      {/* Live Status Toast */}
      {statusMessage && (
        <div
          className={`p-3 rounded-lg border flex items-center justify-between text-xs transition-all ${
            isAssessing
              ? 'bg-amber-950/40 border-amber-500/40 text-amber-300'
              : 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
          }`}
        >
          <div className="flex items-center gap-2">
            {isAssessing && <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>}
            <span>{statusMessage}</span>
          </div>
          {assessment?.heatmap_activity_id && (
            <span className="text-[10px] text-gray-400 font-mono">
              FortyGuard Activity: {assessment.heatmap_activity_id}
            </span>
          )}
        </div>
      )}

      {/* Facility Selector and Trigger */}
      <SiteSelector
        onSelect={setSelectedSite}
        onRunAssessment={handleRunAssessment}
        isAssessing={isAssessing}
      />

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div className="col-span-1 md:col-span-2 lg:col-span-1 xl:col-span-1">
          <RiskCard level={riskCategory} provenance={currentProvenance} />
        </div>

        <TemperatureCard value={currentEnv.temperature} provenance={currentProvenance} />
        <HeatIndexCard value={currentEnv.heat_index} provenance={currentProvenance} />
        <WetBulbCard value={currentEnv.wet_bulb_temperature} provenance={currentProvenance} />
        <HumidityCard value={currentEnv.relative_humidity} provenance={currentProvenance} />
      </div>

      {/* Spatial Visualization + HSE Protocol Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Spatial Thermal Map (Spans 2 columns) */}
        <div className="col-span-1 lg:col-span-2">
          <ThermalMap
            center={mapCenter}
            geoJsonData={assessment?.map_geojson}
            provenance={assessment?.stats?.provenance || currentProvenance}
            onCellSelect={setSelectedCellId}
          />
        </div>

        {/* Operational HSE Protocol Card */}
        <div className="col-span-1">
          <HSEProtocolCard
            workload={workload}
            onWorkloadChange={setWorkload}
            workMinutes={
              explainReport?.what.work_rest_guidance.includes('15 min')
                ? 15
                : explainReport?.what.work_rest_guidance.includes('30 min')
                ? 30
                : explainReport?.what.work_rest_guidance.includes('45 min')
                ? 45
                : 60
            }
            restMinutes={
              explainReport?.what.work_rest_guidance.includes('45 min Rest')
                ? 45
                : explainReport?.what.work_rest_guidance.includes('30 min Rest')
                ? 30
                : explainReport?.what.work_rest_guidance.includes('15 min Rest')
                ? 15
                : 0
            }
            hydrationMl={
              riskCategory === 'Extreme' ? 1000 : riskCategory === 'High' ? 750 : 500
            }
            riskCategory={riskCategory}
            warnings={explainReport?.what.warnings || []}
          />
        </div>
      </div>

      {/* Explainability Triad Report (WHERE / WHY / WHAT) */}
      <ExplainabilityCard report={explainReport} isLoading={loadingExplain} />

      {/* What-If Safety Mitigation Simulator */}
      <WhatIfSimulator
        baselineTemperature={currentEnv.temperature || 38.5}
        baselineWetBulb={currentEnv.wet_bulb_temperature || 28.5}
        baselineSolarGhi={currentEnv.solar_irradiance || 850.0}
        workload={workload}
      />

      {/* Printable HSE Shift Report Modal */}
      <HSEShiftReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        site={selectedSite}
        assessment={assessment}
        report={explainReport}
      />
    </div>
  );
}
