import React from 'react';

export default function AIAssistantPlaceholder() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg flex flex-col h-full min-h-[300px]">
      <div className="p-4 border-b border-gray-800 flex justify-between items-center">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
          <svg className="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          AI Safety Assistant
        </h3>
        <span className="text-xs font-medium text-amber-500 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20">Phase 2</span>
      </div>
      
      <div className="flex-1 p-4 bg-gray-950 flex flex-col justify-end relative">
        <div className="absolute inset-0 flex items-center justify-center p-6 text-center opacity-50">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Automated HSE Recommendations</h4>
            <p className="text-xs text-gray-600">
              Future integration will provide AI-driven mitigation strategies based on real-time HeatGuard data.
            </p>
          </div>
        </div>
        
        <div className="relative mt-auto">
          <div className="flex gap-2">
            <input 
              type="text" 
              disabled 
              placeholder="Ask about safety protocols..." 
              className="flex-1 bg-gray-900 border border-gray-800 text-gray-400 text-sm rounded-lg p-2.5 outline-none cursor-not-allowed"
            />
            <button disabled className="bg-gray-800 border border-gray-700 text-gray-500 rounded-lg px-4 py-2 cursor-not-allowed">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
