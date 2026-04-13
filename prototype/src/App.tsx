import { useState } from 'react';
import LiveLeads from './components/LiveLeads';
import Pipeline from './components/Pipeline';
import Metrics from './components/Metrics';
import VoiceCommand from './components/VoiceCommand';
import CaseDetail from './components/CaseDetail';
import type { Lead } from './types';

type Tab = 'leads' | 'pipeline' | 'metrics' | 'voice';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('leads');
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  const tabs: { id: Tab; label: string }[] = [
    { id: 'leads', label: 'Live Leads' },
    { id: 'pipeline', label: 'Pipeline' },
    { id: 'metrics', label: 'Metrics' },
    { id: 'voice', label: 'Voice Command' },
  ];

  const handleSelectLead = (lead: Lead) => {
    setSelectedLead(lead);
    setActiveTab('leads');
  };

  const handleBack = () => {
    setSelectedLead(null);
  };

  return (
    <div className="min-h-screen bg-navy-900 text-white">
      {/* Header */}
      <header className="bg-navy-800 border-b border-gold/20 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gold rounded-lg flex items-center justify-center">
              <span className="text-navy-900 font-serif font-bold text-xl">Y</span>
            </div>
            <div>
              <h1 className="font-serif font-bold text-xl text-gold">You Became The Money</h1>
              <p className="text-gray-400 text-xs">Command Center • Mr. Garcia</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-xs text-gray-400">Hermes Status</p>
              <p className="text-green-400 text-sm font-medium flex items-center gap-2">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Online
              </p>
            </div>
            <div className="w-8 h-8 bg-navy-700 rounded-full flex items-center justify-center">
              <span className="text-gold font-semibold">DG</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-navy-800 border-b border-gold/10 px-6">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                if (tab.id !== 'leads') setSelectedLead(null);
              }}
              className={`px-6 py-4 font-medium text-sm transition-all border-b-2 ${
                activeTab === tab.id
                  ? 'text-gold border-gold bg-gold/5'
                  : 'text-gray-400 border-transparent hover:text-white hover:bg-navy-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="p-6 max-w-7xl mx-auto">
        {activeTab === 'leads' && selectedLead ? (
          <CaseDetail lead={selectedLead} onBack={handleBack} />
        ) : activeTab === 'leads' ? (
          <LiveLeads onSelectLead={handleSelectLead} />
        ) : activeTab === 'pipeline' ? (
          <Pipeline onSelectLead={handleSelectLead} />
        ) : activeTab === 'metrics' ? (
          <Metrics />
        ) : (
          <VoiceCommand />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-navy-800 border-t border-gold/10 px-6 py-4 mt-8">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <p>Prototype Phase • Wednesday Demo Ready</p>
          <p>Powered by Hermes Agent • Self-Hosted</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
