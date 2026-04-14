import { useState, useEffect } from 'react';
import type { Lead, Metrics } from '../types';
import { mockHermesAPI } from '../api/mockHermes';
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

// BusinessMetrics reserved for financials tab (Week 3)
// interface BusinessMetrics { ... }

export default function CommandCenter({ leads }: CommandCenterProps) {
  const [tab, setTab] = useState<'overview' | 'crm' | 'calls' | 'social' | 'financials' | 'hermes' | 'voice'>('overview');
  const [_metrics, _setMetrics] = useState<Metrics | null>(null);
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
        {(['overview', 'crm', 'calls', 'social', 'financials', 'hermes', 'voice'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all whitespace-nowrap ${
              tab === t
                ? 'bg-gold text-navy-900'
                : 'bg-navy-700 text-gold hover:bg-navy-600'
            }`}
          >
            {t === 'overview' && '📊 Overview'}
            {t === 'crm' && '👥 CRM'}
            {t === 'calls' && '📞 Calls'}
            {t === 'social' && '📱 Social'}
            {t === 'financials' && '💰 Financials'}
            {t === 'hermes' && '🤖 Hermes'}
            {t === 'voice' && '🎤 Voice'}
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

      {/* VOICE Tab */}
      {tab === 'voice' && (
        <VoiceInterface />
      )}
    </div>
  );
}
