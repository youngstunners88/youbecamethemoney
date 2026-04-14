import { useState, useEffect } from 'react';
import type { Lead, Metrics } from '../types';
import {
  mockHermesAPI,
  type GrowthWeek,
  type EconomicsData,
  type HallOfFameProfile,
  type WarmthLead,
} from '../api/mockHermes';
import VoiceInterface from './VoiceInterface';

interface CommandCenterProps {
  leads: Lead[];
}

interface SocialStats {
  platform: 'instagram' | 'facebook';
  followers: number;
  engagement: number;
  reachThisMonth: number;
  postsThisMonth: number;
  topPerformer: string;
}

type TabId = 'overview' | 'crm' | 'calls' | 'social' | 'financials' | 'hermes' | 'voice' | 'growth' | 'hof' | 'warmth';

export default function CommandCenter({ leads }: CommandCenterProps) {
  const [tab, setTab] = useState<TabId>('overview');
  const [_metrics, _setMetrics] = useState<Metrics | null>(null);
  const [growthData, setGrowthData] = useState<GrowthWeek[]>([]);
  const [economics, setEconomics] = useState<EconomicsData | null>(null);
  const [hofProfiles, setHofProfiles] = useState<HallOfFameProfile[]>([]);
  const [warmthLeads, setWarmthLeads] = useState<WarmthLead[]>([]);
  const [socialStats, _setSocialStats] = useState<SocialStats[]>([
    {
      platform: 'instagram',
      followers: 8234,
      engagement: 12.5,
      reachThisMonth: 156230,
      postsThisMonth: 18,
      topPerformer: 'UCC Article Breakdown - 2,340 likes'
    },
    {
      platform: 'facebook',
      followers: 5120,
      engagement: 8.3,
      reachThisMonth: 98450,
      postsThisMonth: 14,
      topPerformer: 'Case Study: From Goods to GODS - 1,234 shares'
    }
  ]);

  useEffect(() => {
    loadMetrics();
    mockHermesAPI.getGrowthData().then(setGrowthData);
    mockHermesAPI.getEconomics().then(setEconomics);
    mockHermesAPI.getHallOfFame().then(setHofProfiles);
    mockHermesAPI.getWarmthLeads().then(setWarmthLeads);
  }, []);

  const loadMetrics = async () => {
    const data = await mockHermesAPI.getMetrics();
    _setMetrics(data);
  };

  const hotLeads = leads.filter(l => l.urgencyScore >= 8).length;
  const warmLeads = leads.filter(l => l.urgencyScore >= 6 && l.urgencyScore < 8).length;
  const callsThisWeek = leads.length; // Mock
  const hermesEfficiency = 84; // Mock percentage

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-serif font-bold text-gold">⚙️ COMMAND CENTER</h1>
            <p className="text-gray-400">System Operations & Business Intelligence</p>
          </div>
          <div className="text-right">
            <p className="text-gray-400 text-sm">Hermes Status</p>
            <p className="text-green-400 font-semibold flex items-center gap-2 justify-end">
              <span className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></span>
              Expanding Growth
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 bg-navy-800 rounded-xl p-2 border border-gold/20 overflow-x-auto">
        {([
          ['overview', '📊 Overview'],
          ['crm', '👥 CRM'],
          ['calls', '📞 Calls'],
          ['social', '📱 Social'],
          ['financials', '💰 Financials'],
          ['hermes', '🤖 Hermes'],
          ['growth', '📈 Growth'],
          ['hof', '🏆 Hall of Fame'],
          ['warmth', '🌡️ Warmth'],
          ['voice', '🎤 Voice'],
        ] as [TabId, string][]).map(([t, label]) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all whitespace-nowrap ${
              tab === t
                ? 'bg-gold text-navy-900'
                : 'bg-navy-700 text-gold hover:bg-navy-600'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* OVERVIEW Tab */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Hot Leads */}
          <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-red-400 text-sm font-semibold">🔥 HOT LEADS</p>
                <p className="text-3xl font-bold text-white mt-2">{hotLeads}</p>
              </div>
              <span className="text-red-500 text-2xl">↑</span>
            </div>
            <p className="text-red-300 text-xs mt-3">Ready to hire, immediate action</p>
          </div>

          {/* Warm Leads */}
          <div className="bg-orange-900/20 border border-orange-500/30 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-orange-400 text-sm font-semibold">🌡️ WARM LEADS</p>
                <p className="text-3xl font-bold text-white mt-2">{warmLeads}</p>
              </div>
              <span className="text-orange-500 text-2xl">→</span>
            </div>
            <p className="text-orange-300 text-xs mt-3">Problem-aware, nurturing</p>
          </div>

          {/* Calls This Week */}
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-blue-400 text-sm font-semibold">📞 CALLS THIS WEEK</p>
                <p className="text-3xl font-bold text-white mt-2">{callsThisWeek}</p>
              </div>
              <span className="text-blue-500 text-2xl">📈</span>
            </div>
            <p className="text-blue-300 text-xs mt-3">Outbound + inbound combined</p>
          </div>

          {/* Hermes Efficiency */}
          <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-emerald-400 text-sm font-semibold">🤖 HERMES EFFICIENCY</p>
                <p className="text-3xl font-bold text-white mt-2">{hermesEfficiency}%</p>
              </div>
              <span className="text-emerald-500 text-2xl">⚡</span>
            </div>
            <p className="text-emerald-300 text-xs mt-3">Lead qualification automation</p>
          </div>
        </div>
      )}

      {/* CRM Tab */}
      {tab === 'crm' && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold mb-4 text-lg">Lead Pipeline</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { status: 'NEW', count: leads.filter(l => l.status === 'new').length, color: 'bg-blue-600' },
                { status: 'QUALIFIED', count: leads.filter(l => l.status === 'qualified').length, color: 'bg-yellow-600' },
                { status: 'CONSULTING', count: leads.filter(l => l.status === 'consulting').length, color: 'bg-orange-600' },
                { status: 'RETAINED', count: leads.filter(l => l.status === 'retained').length, color: 'bg-green-600' },
                { status: 'CLOSED', count: leads.filter(l => l.status === 'closed-won' || l.status === 'closed-lost').length, color: 'bg-purple-600' }
              ].map((stage) => (
                <div key={stage.status} className={`${stage.color} rounded-lg p-4 text-white text-center`}>
                  <p className="text-2xl font-bold">{stage.count}</p>
                  <p className="text-xs font-semibold mt-1">{stage.status}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Interactions */}
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold mb-4 text-lg">Recent Interactions</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {leads.slice(0, 5).map((lead) => (
                <div key={lead.id} className="bg-navy-700 rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <p className="text-white font-semibold">{lead.name}</p>
                    <p className="text-gray-400 text-sm">{lead.serviceType}</p>
                  </div>
                  <span className="text-xs text-gray-500">{new Date(lead.timestamp).toLocaleDateString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* CALLS Tab */}
      {tab === 'calls' && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold mb-4 text-lg">📞 Call Analytics (Mragerita Agent)</h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-navy-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm">Total Calls</p>
                <p className="text-2xl font-bold text-white mt-2">247</p>
              </div>
              <div className="bg-navy-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm">Avg Duration</p>
                <p className="text-2xl font-bold text-white mt-2">6m 42s</p>
              </div>
              <div className="bg-navy-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm">Completed</p>
                <p className="text-2xl font-bold text-emerald-400 mt-2">89%</p>
              </div>
              <div className="bg-navy-700 rounded-lg p-4">
                <p className="text-gray-400 text-sm">Failed</p>
                <p className="text-2xl font-bold text-red-400 mt-2">11%</p>
              </div>
            </div>

            {/* Call Transcript Preview */}
            <div className="bg-navy-900 rounded-lg p-4">
              <p className="text-gray-400 text-sm mb-3">📝 Recent Call Transcript (Sample)</p>
              <div className="space-y-2 text-sm max-h-48 overflow-y-auto">
                <div className="text-blue-400">
                  <strong>Mragerita:</strong> "Good afternoon, this is Mragerita calling from You Became The Money on behalf of Daniel Garcia."
                </div>
                <div className="text-gray-300">
                  <strong>Prospect:</strong> "Hi, yes, I was actually waiting for your call."
                </div>
                <div className="text-blue-400">
                  <strong>Mragerita:</strong> "Excellent! So tell me, what's your current situation with debt or commercial matters?"
                </div>
                <div className="text-gray-300">
                  <strong>Prospect:</strong> "I've been dealing with securitization issues and I read your ebook. I'm ready to move forward."
                </div>
                <div className="text-green-400 font-semibold mt-3">
                  ✅ Temperature Detected: HOT
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SOCIAL Tab */}
      {tab === 'social' && (
        <div className="space-y-4">
          {socialStats.map((social) => (
            <div key={social.platform} className="bg-navy-800 border border-gold/20 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gold font-semibold text-lg">
                  {social.platform === 'instagram' ? '📸 Instagram' : '👍 Facebook'}
                </h3>
                <a
                  href={social.platform === 'instagram'
                    ? 'https://www.instagram.com/youbecamethemoney?igsh=cXNkb3V0MWwzczd0'
                    : 'https://www.facebook.com/share/18VNhWZkFE/?mibextid=wwXIfr'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gold hover:text-gold-light text-sm"
                >
                  View Profile →
                </a>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <div className="bg-navy-700 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Followers</p>
                  <p className="text-2xl font-bold text-white mt-2">{social.followers.toLocaleString()}</p>
                </div>
                <div className="bg-navy-700 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Engagement</p>
                  <p className="text-2xl font-bold text-orange-400 mt-2">{social.engagement}%</p>
                </div>
                <div className="bg-navy-700 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">This Month Reach</p>
                  <p className="text-2xl font-bold text-white mt-2">{(social.reachThisMonth / 1000).toFixed(0)}K</p>
                </div>
                <div className="bg-navy-700 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Posts</p>
                  <p className="text-2xl font-bold text-blue-400 mt-2">{social.postsThisMonth}</p>
                </div>
                <div className="bg-navy-700 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Top Post</p>
                  <p className="text-xs font-bold text-gold mt-2 line-clamp-2">{social.topPerformer}</p>
                </div>
              </div>

              <div className="bg-gold/10 border border-gold/20 rounded-lg p-4">
                <p className="text-gold text-sm font-semibold mb-2">💡 Content Strategy</p>
                <p className="text-gray-300 text-sm">
                  {social.platform === 'instagram'
                    ? 'Focus on educational carousel posts about UCC Articles. Short-form video content is outperforming static posts by 45%. Reels get 3x more engagement than photos.'
                    : 'Case study videos driving highest engagement. Community posts generate more shares than promotional content. Live Q&A sessions averaging 200+ viewers.'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* FINANCIALS Tab */}
      {tab === 'financials' && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold mb-4 text-lg">💰 Business Financials</h3>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-lg p-4">
                <p className="text-emerald-400 text-sm font-semibold">Monthly Revenue</p>
                <p className="text-3xl font-bold text-white mt-2">$47,320</p>
                <p className="text-emerald-300 text-xs mt-2">↑ 23% vs last month</p>
              </div>
              <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-4">
                <p className="text-orange-400 text-sm font-semibold">Acquisition Cost</p>
                <p className="text-3xl font-bold text-white mt-2">$8,450</p>
                <p className="text-orange-300 text-xs mt-2">21 leads acquired this month</p>
              </div>
              <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <p className="text-blue-400 text-sm font-semibold">ROI</p>
                <p className="text-3xl font-bold text-white mt-2">460%</p>
                <p className="text-blue-300 text-xs mt-2">Per dollar spent</p>
              </div>
              <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
                <p className="text-purple-400 text-sm font-semibold">Avg Case Value</p>
                <p className="text-3xl font-bold text-white mt-2">$3,200</p>
                <p className="text-purple-300 text-xs mt-2">UCC Discharge cases</p>
              </div>
              <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
                <p className="text-cyan-400 text-sm font-semibold">Conversion Rate</p>
                <p className="text-3xl font-bold text-white mt-2">18.5%</p>
                <p className="text-cyan-300 text-xs mt-2">Inquiry to client</p>
              </div>
              <div className="bg-rose-900/20 border border-rose-500/30 rounded-lg p-4">
                <p className="text-rose-400 text-sm font-semibold">Operating Margin</p>
                <p className="text-3xl font-bold text-white mt-2">72%</p>
                <p className="text-rose-300 text-xs mt-2">After all expenses</p>
              </div>
            </div>

            {/* Revenue Breakdown */}
            <div className="bg-navy-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm font-semibold mb-3">Revenue by Service Type</p>
              <div className="space-y-2">
                {[
                  { service: 'UCC Discharge', revenue: 18700, pct: 40 },
                  { service: 'Securitization Review', revenue: 12450, pct: 26 },
                  { service: 'Trust Verification', revenue: 10280, pct: 22 },
                  { service: 'Banking Law', revenue: 5890, pct: 12 }
                ].map((item) => (
                  <div key={item.service}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300">{item.service}</span>
                      <span className="text-gold font-semibold">${item.revenue.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-navy-900 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-gold to-amber-500 h-2 rounded-full"
                        style={{ width: `${item.pct}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* HERMES Tab */}
      {tab === 'hermes' && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold mb-4 text-lg">🤖 Hermes AI Growth & Expansion</h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-lg p-4">
                <p className="text-emerald-400 text-sm font-semibold">Efficiency Gain</p>
                <p className="text-3xl font-bold text-white mt-2">84%</p>
                <p className="text-emerald-300 text-xs mt-2">Automation of intake process</p>
              </div>
              <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                <p className="text-blue-400 text-sm font-semibold">Leads Qualified</p>
                <p className="text-3xl font-bold text-white mt-2">142</p>
                <p className="text-blue-300 text-xs mt-2">This month by Hermes</p>
              </div>
              <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
                <p className="text-purple-400 text-sm font-semibold">Skills Deployed</p>
                <p className="text-3xl font-bold text-white mt-2">5</p>
                <p className="text-purple-300 text-xs mt-2">Custom FastMCP skills</p>
              </div>
              <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-4">
                <p className="text-orange-400 text-sm font-semibold">Growth Rate</p>
                <p className="text-3xl font-bold text-white mt-2">127%</p>
                <p className="text-orange-300 text-xs mt-2">YoY improvement</p>
              </div>
            </div>

            {/* Hermes Strategy */}
            <div className="space-y-4">
              <div className="bg-navy-700 rounded-lg p-4">
                <p className="text-gold text-sm font-semibold mb-2">📋 Current Implementations</p>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>✅ Retell Voice Agent (Mragerita) - Lead qualification at scale</li>
                  <li>✅ Lead Temperature Scoring - Automated hot/warm/luke/cold detection</li>
                  <li>✅ SMS Fallback System - 3-second phone timeout → SMS → email</li>
                  <li>✅ CRM Integration - Real-time lead pipeline visibility</li>
                  <li>🔄 Social Media Analytics - Auto-pull from Instagram & Facebook (coming)</li>
                </ul>
              </div>

              <div className="bg-navy-700 rounded-lg p-4">
                <p className="text-gold text-sm font-semibold mb-2">🚀 Next Growth Strategies</p>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>1. Deploy Claude API for intelligent transcript analysis</li>
                  <li>2. Build skill system for case pattern learning & automation</li>
                  <li>3. Integrate calendar API for auto-scheduling consultations</li>
                  <li>4. Add email drafter skill for personalized outreach at scale</li>
                  <li>5. Implement P2P inference for cost-free lead scoring</li>
                </ul>
              </div>

              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-lg p-4">
                <p className="text-emerald-400 text-sm font-semibold mb-2">💰 Projected Impact (3 months)</p>
                <p className="text-gray-300 text-sm">
                  • Lead intake volume: <strong>+200%</strong><br/>
                  • Acquisition cost: <strong>-35%</strong> (automation)<br/>
                  • Conversion rate: <strong>+12%</strong> (better qualification)<br/>
                  • Revenue potential: <strong>$120K+</strong> monthly<br/>
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* GROWTH Tab — Layer 3 trajectory */}
      {tab === 'growth' && (
        <div className="space-y-4">
          {/* Economics KPIs */}
          {economics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-5">
                <p className="text-emerald-400 text-xs font-semibold uppercase tracking-wide">Current Close Rate</p>
                <p className="text-3xl font-bold text-white mt-2">{economics.currentCloseRate}%</p>
                <p className="text-emerald-300 text-xs mt-1">Week 1 baseline</p>
              </div>
              <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-5">
                <p className="text-blue-400 text-xs font-semibold uppercase tracking-wide">Projected (8 Weeks)</p>
                <p className="text-3xl font-bold text-white mt-2">{economics.projectedCloseRate}%</p>
                <p className="text-blue-300 text-xs mt-1">+{(economics.projectedCloseRate - economics.currentCloseRate).toFixed(1)}% via Layer 3</p>
              </div>
              <div className="bg-gold/10 border border-gold/30 rounded-xl p-5">
                <p className="text-gold text-xs font-semibold uppercase tracking-wide">Revenue Added / Week</p>
                <p className="text-3xl font-bold text-white mt-2">${economics.revenueAddedPerWeek.toLocaleString()}</p>
                <p className="text-amber-300 text-xs mt-1">At full trajectory</p>
              </div>
              <div className="bg-purple-900/20 border border-purple-500/30 rounded-xl p-5">
                <p className="text-purple-400 text-xs font-semibold uppercase tracking-wide">ROI Multiple</p>
                <p className="text-3xl font-bold text-white mt-2">{(economics.roiMultiple / 1_000_000).toFixed(1)}M×</p>
                <p className="text-purple-300 text-xs mt-1">Revenue vs API cost</p>
              </div>
            </div>
          )}

          {/* 8-Week Trajectory Table */}
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold text-lg mb-4">📈 8-Week Layer 3 Learning Trajectory</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-400 border-b border-navy-600">
                    <th className="text-left py-2 pr-4">Week</th>
                    <th className="text-right py-2 pr-4">Close Rate</th>
                    <th className="text-right py-2 pr-4">Warmth Avg</th>
                    <th className="text-right py-2 pr-4">Calls / Wk</th>
                    <th className="text-right py-2">Weekly Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {growthData.map((row, i) => {
                    const maxRevenue = Math.max(...growthData.map(r => r.revenue));
                    const pct = Math.round((row.revenue / maxRevenue) * 100);
                    return (
                      <tr key={row.week} className="border-b border-navy-700 hover:bg-navy-700/40 transition-colors">
                        <td className="py-3 pr-4 text-gray-300 font-medium">{row.label}</td>
                        <td className="py-3 pr-4 text-right">
                          <span className={`font-semibold ${i === 0 ? 'text-gray-300' : 'text-emerald-400'}`}>
                            {row.closeRate}%
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-right text-blue-300">{row.warmthAvg}</td>
                        <td className="py-3 pr-4 text-right text-gray-300">{row.callsPerWeek}</td>
                        <td className="py-3 text-right">
                          <div className="flex items-center justify-end gap-3">
                            <div className="w-24 bg-navy-900 rounded-full h-1.5 hidden md:block">
                              <div
                                className="bg-gradient-to-r from-gold to-amber-400 h-1.5 rounded-full"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                            <span className="text-gold font-semibold">${row.revenue.toLocaleString()}</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className="mt-4 bg-gold/10 border border-gold/20 rounded-lg p-3 text-xs text-gold">
              💡 Layer 3 learns from every interview, call, and case outcome. Close rate compounds weekly as behavioral patterns improve Margarita's targeting.
            </div>
          </div>

          {/* Economics detail */}
          {economics && (
            <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
              <h3 className="text-gold font-semibold text-lg mb-4">💡 Unit Economics</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  { label: 'Leads / Week', value: economics.leadsPerWeek.toString(), color: 'text-white' },
                  { label: 'Cost per Lead (API)', value: `$${economics.costPerLead.toFixed(2)}`, color: 'text-emerald-400' },
                  { label: 'Avg Case Value', value: `$${economics.avgCaseValue.toLocaleString()}`, color: 'text-gold' },
                  { label: 'Weekly API Cost', value: `$${economics.weeklyApiCost.toFixed(3)}`, color: 'text-emerald-400' },
                  { label: 'Current Close Rate', value: `${economics.currentCloseRate}%`, color: 'text-white' },
                  { label: 'Projected Close Rate', value: `${economics.projectedCloseRate}%`, color: 'text-blue-400' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-navy-700 rounded-lg p-4">
                    <p className="text-gray-400 text-xs mb-1">{label}</p>
                    <p className={`text-xl font-bold ${color}`}>{value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* HALL OF FAME Tab */}
      {tab === 'hof' && (
        <div className="space-y-4">
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-gold font-semibold text-lg">🏆 Hall of Fame — Case Outcomes</h3>
                <p className="text-gray-400 text-sm mt-1">Anonymized wins curated by Hermes from closed cases</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gold">{hofProfiles.length}</p>
                <p className="text-gray-400 text-xs">Cases featured</p>
              </div>
            </div>

            <div className="space-y-4">
              {hofProfiles.map((profile) => {
                const outcomeColor = profile.case_outcome === 'won'
                  ? 'bg-emerald-900/30 border-emerald-500/40'
                  : profile.case_outcome === 'settled'
                  ? 'bg-blue-900/30 border-blue-500/40'
                  : 'bg-purple-900/30 border-purple-500/40';
                const outcomeLabel = profile.case_outcome === 'won' ? '✅ Won'
                  : profile.case_outcome === 'settled' ? '🤝 Settled' : '↗️ Referred';
                return (
                  <div key={profile.id} className={`border rounded-xl p-5 ${outcomeColor}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <p className="text-white font-bold text-base">{profile.headline}</p>
                        <div className="flex gap-3 mt-1 flex-wrap">
                          <span className="text-xs text-gray-400">{profile.service_type}</span>
                          <span className="text-xs text-gray-400">•</span>
                          <span className="text-xs text-gray-400">{profile.jurisdiction}</span>
                          <span className="text-xs text-gray-400">•</span>
                          <span className="text-xs text-gray-400">{new Date(profile.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="text-right ml-4 shrink-0">
                        <p className="text-xs font-semibold text-gray-300">{outcomeLabel}</p>
                        <p className="text-gold font-bold text-lg">${profile.case_value.toLocaleString()}</p>
                        <p className="text-xs text-gray-400">Confidence {profile.confidence_score}%</p>
                      </div>
                    </div>

                    <blockquote className="text-gray-300 text-sm italic border-l-2 border-gold/40 pl-3 mb-3">
                      "{profile.testimonial}"
                    </blockquote>

                    <div className="flex gap-2 flex-wrap">
                      {profile.key_signals.map((sig) => (
                        <span key={sig} className="text-xs bg-navy-700 text-gold border border-gold/20 rounded-full px-3 py-0.5">
                          {sig}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {hofProfiles.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <p className="text-4xl mb-3">🏆</p>
                <p className="font-medium">No cases in Hall of Fame yet.</p>
                <p className="text-sm mt-1">Cases appear here when marked as won / settled / referred.</p>
              </div>
            )}
          </div>

          <div className="bg-gold/10 border border-gold/20 rounded-xl p-4 text-sm text-gold">
            💡 <strong>How it works:</strong> When Hermes closes a case, the <code className="bg-navy-700 px-1 rounded text-xs">hall_of_fame_curator</code> skill extracts key quotes, scores evidence confidence, and generates an anonymized testimonial — automatically.
          </div>
        </div>
      )}

      {/* WARMTH Tab — Lemonslice interview-scored leads */}
      {tab === 'warmth' && (
        <div className="space-y-4">
          {/* Summary bar */}
          <div className="grid grid-cols-3 gap-4">
            {(['hot', 'warm', 'cold'] as const).map((tier) => {
              const count = warmthLeads.filter(l => l.warmthTier === tier).length;
              const cfg = {
                hot: { color: 'text-red-400', bg: 'bg-red-900/20 border-red-500/30', icon: '🔥', label: 'Hot' },
                warm: { color: 'text-orange-400', bg: 'bg-orange-900/20 border-orange-500/30', icon: '🌡️', label: 'Warm' },
                cold: { color: 'text-blue-400', bg: 'bg-blue-900/20 border-blue-500/30', icon: '❄️', label: 'Cold' },
              }[tier];
              return (
                <div key={tier} className={`border rounded-xl p-5 ${cfg.bg}`}>
                  <p className={`text-sm font-semibold ${cfg.color}`}>{cfg.icon} {cfg.label}</p>
                  <p className="text-3xl font-bold text-white mt-2">{count}</p>
                  <p className="text-xs text-gray-400 mt-1">Interview-qualified</p>
                </div>
              );
            })}
          </div>

          {/* Leads table */}
          <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
            <h3 className="text-gold font-semibold text-lg mb-4">🌡️ Warmth Scores — Lemonslice Interview Data</h3>
            <div className="space-y-3">
              {warmthLeads.map((lead) => {
                const tierCfg = {
                  hot: { bar: 'from-red-600 to-red-400', badge: 'bg-red-900/40 text-red-300 border-red-500/30', icon: '🔥' },
                  warm: { bar: 'from-orange-600 to-amber-400', badge: 'bg-orange-900/40 text-orange-300 border-orange-500/30', icon: '🌡️' },
                  cold: { bar: 'from-blue-700 to-blue-400', badge: 'bg-blue-900/40 text-blue-300 border-blue-500/30', icon: '❄️' },
                }[lead.warmthTier];
                const hoursAgo = Math.round((Date.now() - new Date(lead.timestamp).getTime()) / 3600e3);
                return (
                  <div key={lead.id} className="bg-navy-700 rounded-xl p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-white font-semibold">{lead.name}</p>
                        <p className="text-gray-400 text-xs">{lead.serviceType} • {lead.jurisdiction} • {hoursAgo}h ago</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-semibold border rounded-full px-3 py-0.5 ${tierCfg.badge}`}>
                          {tierCfg.icon} {lead.warmthTier.toUpperCase()}
                        </span>
                        <span className="text-gold font-bold text-lg">{lead.warmthScore}</span>
                      </div>
                    </div>

                    {/* Warmth bar */}
                    <div className="w-full bg-navy-900 rounded-full h-2 mb-2">
                      <div
                        className={`bg-gradient-to-r ${tierCfg.bar} h-2 rounded-full transition-all`}
                        style={{ width: `${lead.warmthScore}%` }}
                      />
                    </div>

                    <p className="text-gray-400 text-xs italic">"{lead.behaviorSummary}"</p>

                    <div className="flex gap-2 mt-2">
                      <span className="text-xs bg-navy-800 text-gray-400 rounded px-2 py-0.5 capitalize">{lead.status}</span>
                      <span className="text-xs bg-navy-800 text-gray-400 rounded px-2 py-0.5">Urgency {lead.urgencyScore}/10</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {warmthLeads.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <p className="text-4xl mb-3">🌡️</p>
                <p className="font-medium">No interview data yet.</p>
                <p className="text-sm mt-1">Send leads to the Lemonslice portal to see warmth scores here.</p>
              </div>
            )}
          </div>

          <div className="bg-gold/10 border border-gold/20 rounded-xl p-4 text-sm text-gold">
            💡 <strong>How warmth scores work:</strong> Each lead completes the Lemonslice interview. The <code className="bg-navy-700 px-1 rounded text-xs">interview_analyzer</code> skill scores tone confidence, urgency, knowledge level, and hesitation — then updates warmth (+30 to −20) before Margarita's call.
          </div>
        </div>
      )}

      {/* VOICE Tab */}
      {tab === 'voice' && (
        <VoiceInterface />
      )}
    </div>
  );
}
