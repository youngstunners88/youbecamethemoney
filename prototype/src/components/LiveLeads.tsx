import { useState, useEffect } from 'react';
import type { Lead, ServiceType } from '../types';
import { mockHermesAPI, simulateNewLead } from '../api/mockHermes';

const serviceColors: Record<ServiceType, string> = {
  'Commercial Law': 'bg-blue-500',
  'UCC Discharge': 'bg-purple-500',
  'Securitization Review': 'bg-indigo-500',
  'Trust Verification': 'bg-emerald-500',
  'Secured Party Creditor': 'bg-amber-500',
  'Banking Law': 'bg-rose-500',
  'Corporate Structuring': 'bg-cyan-500'
};

const statusColors: Record<string, string> = {
  new: 'text-blue-400',
  qualified: 'text-yellow-400',
  consulting: 'text-orange-400',
  retained: 'text-green-400',
  'closed-won': 'text-emerald-400',
  'closed-lost': 'text-red-400'
};

export default function LiveLeads() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filterService, setFilterService] = useState<ServiceType | 'all'>('all');
  const [minUrgency, setMinUrgency] = useState<number>(1);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    const data = await mockHermesAPI.getLeads();
    setLeads(data);
  };

  const startSimulation = () => {
    setIsSimulating(true);
    const interval = setInterval(() => {
      const newLead = simulateNewLead();
      setLeads(prev => [newLead, ...prev]);
    }, 10000);
    
    setTimeout(() => {
      clearInterval(interval);
      setIsSimulating(false);
    }, 120000);
  };

  const filteredLeads = leads.filter(lead => {
    const serviceMatch = filterService === 'all' || lead.serviceType === filterService;
    const urgencyMatch = lead.urgencyScore >= minUrgency;
    return serviceMatch && urgencyMatch;
  });

  const serviceTypes: ServiceType[] = [
    'Commercial Law', 'UCC Discharge', 'Securitization Review',
    'Trust Verification', 'Secured Party Creditor', 'Banking Law', 'Corporate Structuring'
  ];

  return (
    <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-serif font-bold text-gold">Live Leads</h2>
          <p className="text-gray-400 text-sm">Real-time intake from all channels</p>
        </div>
        <div className="flex items-center gap-4">
          {isSimulating && (
            <span className="flex items-center gap-2 text-green-400 text-sm">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              Simulating real-time...
            </span>
          )}
          <button
            onClick={startSimulation}
            disabled={isSimulating}
            className="px-4 py-2 bg-gold text-navy-900 font-semibold rounded-lg hover:bg-gold-light transition-colors disabled:opacity-50"
          >
            Simulate Live
          </button>
          <span className="text-3xl font-bold text-white">{filteredLeads.length}</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 mb-6">
        <select
          value={filterService}
          onChange={(e) => setFilterService(e.target.value as ServiceType | 'all')}
          className="bg-navy-900 border border-gold/30 text-white px-4 py-2 rounded-lg focus:outline-none focus:border-gold"
        >
          <option value="all">All Services</option>
          {serviceTypes.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        
        <div className="flex items-center gap-3">
          <span className="text-gray-400 text-sm">Min Urgency:</span>
          <input
            type="range"
            min="1"
            max="10"
            value={minUrgency}
            onChange={(e) => setMinUrgency(Number(e.target.value))}
            className="w-32 accent-gold"
          />
          <span className="text-gold font-bold w-6">{minUrgency}</span>
        </div>
      </div>

      <div className="grid gap-4 max-h-[600px] overflow-y-auto">
        {filteredLeads.slice(0, 20).map((lead) => (
          <div
            key={lead.id}
            className="bg-navy-900/50 border border-gold/10 rounded-lg p-4 hover:border-gold/30 transition-all"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${serviceColors[lead.serviceType]}`}></div>
                <span className="font-semibold text-white">{lead.name}</span>
                <span className={`text-xs px-2 py-1 rounded-full bg-navy-700 ${statusColors[lead.status]}`}>
                  {lead.status}
                </span>
              </div>
              <span className="text-gray-500 text-sm">
                {new Date(lead.timestamp).toLocaleTimeString()}
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-sm mb-3">
              <div>
                <span className="text-gray-500">Service:</span>
                <p className="text-gray-300">{lead.serviceType}</p>
              </div>
              <div>
                <span className="text-gray-500">Source:</span>
                <p className="text-gray-300 capitalize">{lead.source}</p>
              </div>
              <div>
                <span className="text-gray-500">Urgency:</span>
                <div className="flex items-center gap-1">
                  <div className="flex gap-0.5">
                    {Array.from({ length: 10 }).map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 h-4 rounded-sm ${i < lead.urgencyScore ? 'bg-red-500' : 'bg-navy-700'}`}
                      />
                    ))}
                  </div>
                  <span className="text-gold font-bold ml-2">{lead.urgencyScore}</span>
                </div>
              </div>
            </div>
            
            {lead.message && (
              <p className="text-gray-400 text-sm italic">"{lead.message}"</p>
            )}
            
            <div className="flex gap-2 mt-3">
              {lead.phone && (
                <span className="text-xs text-gray-500">{lead.phone}</span>
              )}
              {lead.email && (
                <span className="text-xs text-gray-500">{lead.email}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
