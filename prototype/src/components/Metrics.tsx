import { useState, useEffect } from 'react';
import type { Metrics as MetricsType, LeadStatus } from '../types';
import { mockHermesAPI } from '../api/mockHermes';

export default function Metrics() {
  const [metrics, setMetrics] = useState<MetricsType | null>(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    const data = await mockHermesAPI.getMetrics();
    setMetrics(data);
  };

  if (!metrics) return <div className="text-white">Loading...</div>;

  const statusLabels: Record<LeadStatus, string> = {
    new: 'New',
    qualified: 'Qualified',
    consulting: 'Consulting',
    retained: 'Retained',
    'closed-won': 'Closed Won',
    'closed-lost': 'Closed Lost'
  };

  const statusColors: Record<LeadStatus, string> = {
    new: 'bg-blue-500',
    qualified: 'bg-yellow-500',
    consulting: 'bg-orange-500',
    retained: 'bg-green-500',
    'closed-won': 'bg-emerald-500',
    'closed-lost': 'bg-red-500'
  };

  const maxCount = Math.max(...Object.values(metrics.leadsByStatus));

  return (
    <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-serif font-bold text-gold">Metrics</h2>
          <p className="text-gray-400 text-sm">Performance overview</p>
        </div>
        <button
          onClick={loadMetrics}
          className="px-4 py-2 bg-navy-700 text-white rounded-lg hover:bg-navy-600 transition-colors text-sm"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-navy-900/50 border border-gold/10 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Total Leads</p>
          <p className="text-3xl font-bold text-white">{metrics.totalLeads}</p>
          <p className="text-green-400 text-xs mt-1">+12% this week</p>
        </div>
        
        <div className="bg-navy-900/50 border border-gold/10 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Conversion Rate</p>
          <p className="text-3xl font-bold text-white">{metrics.conversionRate}%</p>
          <p className="text-gray-500 text-xs mt-1">Industry avg: 8%</p>
        </div>
        
        <div className="bg-navy-900/50 border border-gold/10 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Avg Case Value</p>
          <p className="text-3xl font-bold text-white">${metrics.avgCaseValue.toLocaleString()}</p>
          <p className="text-green-400 text-xs mt-1">+5% this month</p>
        </div>
        
        <div className="bg-navy-900/50 border border-gold/10 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Pipeline Value</p>
          <p className="text-3xl font-bold text-gold">${metrics.pipelineValue.toLocaleString()}</p>
          <p className="text-gray-500 text-xs mt-1">Active deals</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-navy-900/30 border border-gold/10 rounded-lg p-4">
          <h3 className="font-semibold text-white mb-4">Lead Distribution</h3>
          <div className="space-y-3">
            {(Object.entries(metrics.leadsByStatus) as [LeadStatus, number][]).map(([status, count]) => (
              <div key={status} className="flex items-center gap-3">
                <span className="text-gray-400 text-sm w-24">{statusLabels[status]}</span>
                <div className="flex-1 bg-navy-700 rounded-full h-4 overflow-hidden">
                  <div
                    className={`${statusColors[status]} h-full rounded-full transition-all duration-500`}
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  />
                </div>
                <span className="text-white font-medium w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-navy-900/30 border border-gold/10 rounded-lg p-4">
          <h3 className="font-semibold text-white mb-4">Key Insights</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-gold rounded-full mt-2"></div>
              <div>
                <p className="text-white text-sm">Average intake to consultation: <span className="font-bold">{metrics.avgIntakeToConsultDays} days</span></p>
                <p className="text-gray-500 text-xs">Target: 3 days</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="text-white text-sm">Conversion rate is <span className="font-bold">{metrics.conversionRate > 8 ? 'above' : 'below'} industry average</span></p>
                <p className="text-gray-500 text-xs">Keep qualifying high-urgency leads</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-white text-sm">Pipeline health: <span className="font-bold">Strong</span></p>
                <p className="text-gray-500 text-xs">{metrics.leadsByStatus.qualified + metrics.leadsByStatus.consulting} leads in active stages</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
