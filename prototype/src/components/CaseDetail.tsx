import { useState, useEffect } from 'react';
import type { Lead, Case, InteractionLog } from '../types';
import { mockHermesAPI } from '../api/mockHermes';

interface CaseDetailProps {
  lead: Lead;
  onBack: () => void;
}

const serviceColors: Record<string, string> = {
  'Commercial Law': 'text-blue-400 bg-blue-400/10 border-blue-400/30',
  'UCC Discharge': 'text-purple-400 bg-purple-400/10 border-purple-400/30',
  'Securitization Review': 'text-indigo-400 bg-indigo-400/10 border-indigo-400/30',
  'Trust Verification': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
  'Secured Party Creditor': 'text-amber-400 bg-amber-400/10 border-amber-400/30',
  'Banking Law': 'text-rose-400 bg-rose-400/10 border-rose-400/30',
  'Corporate Structuring': 'text-cyan-400 bg-cyan-400/10 border-cyan-400/30',
};

const statusFlow = ['new', 'qualified', 'consulting', 'retained', 'closed-won'];

const statusLabels: Record<string, string> = {
  new: 'New Intake',
  qualified: 'Qualified',
  consulting: 'Consulting',
  retained: 'Retained',
  'closed-won': 'Closed Won',
  'closed-lost': 'Closed Lost',
};

export default function CaseDetail({ lead, onBack }: CaseDetailProps) {
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [interactions, setInteractions] = useState<InteractionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [notes, setNotes] = useState<{ text: string; timestamp: string }[]>([]);

  useEffect(() => {
    loadData();
  }, [lead.id]);

  const loadData = async () => {
    setLoading(true);
    const [cases, logs] = await Promise.all([
      mockHermesAPI.getCases(),
      mockHermesAPI.getInteractions(),
    ]);
    const leadCase = cases.find((c) => c.leadId === lead.id) || null;
    const leadLogs = logs.filter((l) => l.leadId === lead.id);
    // Add synthetic Hermes intake log
    if (leadLogs.length === 0) {
      leadLogs.push({
        timestamp: lead.timestamp,
        platform: lead.source,
        message: lead.message || 'Initial inquiry',
        hermesResponse: `Thank you for reaching out about ${lead.serviceType}. I've captured your inquiry (urgency: ${lead.urgencyScore}/10). Daniel Garcia will review within 24 hours.`,
        leadId: lead.id,
      });
    }
    setCaseData(leadCase);
    setInteractions(leadLogs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()));
    setLoading(false);
  };

  const addNote = () => {
    if (!newNote.trim()) return;
    setNotes((prev) => [{ text: newNote, timestamp: new Date().toISOString() }, ...prev]);
    setNewNote('');
  };

  const urgencyColor =
    lead.urgencyScore >= 8
      ? 'text-red-400'
      : lead.urgencyScore >= 5
      ? 'text-yellow-400'
      : 'text-green-400';

  const currentStepIndex = statusFlow.indexOf(lead.status);

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-8 bg-navy-700 rounded w-1/3"></div>
        <div className="h-32 bg-navy-800 rounded-xl border border-gold/20"></div>
        <div className="h-48 bg-navy-800 rounded-xl border border-gold/20"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button + header */}
      <div className="flex items-center gap-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Leads
        </button>
        <span className="text-gray-600">|</span>
        <h2 className="text-2xl font-serif font-bold text-gold">{lead.name}</h2>
        <span className={`text-xs px-3 py-1 rounded-full border ${serviceColors[lead.serviceType] || 'text-gray-400 border-gray-600'}`}>
          {lead.serviceType}
        </span>
      </div>

      {/* Lead summary card */}
      <div className="bg-navy-800 rounded-xl border border-gold/20 p-6 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p className="text-gray-500 text-xs mb-1">Urgency Score</p>
          <p className={`text-3xl font-bold ${urgencyColor}`}>{lead.urgencyScore}<span className="text-base text-gray-500">/10</span></p>
        </div>
        <div>
          <p className="text-gray-500 text-xs mb-1">Source</p>
          <p className="text-white font-semibold capitalize">{lead.source}</p>
          <p className="text-gray-500 text-xs">{new Date(lead.timestamp).toLocaleDateString()}</p>
        </div>
        <div>
          <p className="text-gray-500 text-xs mb-1">Contact</p>
          {lead.phone && <p className="text-white text-sm">{lead.phone}</p>}
          {lead.email && <p className="text-gray-400 text-xs">{lead.email}</p>}
        </div>
        <div>
          <p className="text-gray-500 text-xs mb-1">Est. Case Value</p>
          <p className="text-gold text-2xl font-bold">
            ${(lead.urgencyScore * 2500).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Pipeline progress */}
      <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
        <h3 className="font-semibold text-white mb-4">Pipeline Progress</h3>
        {lead.status === 'closed-lost' ? (
          <div className="text-center py-4">
            <span className="text-red-400 font-semibold">Closed — Lost</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            {statusFlow.map((step, idx) => (
              <div key={step} className="flex items-center gap-2 flex-1">
                <div className="flex-1">
                  <div
                    className={`h-2 rounded-full ${
                      idx <= currentStepIndex ? 'bg-gold' : 'bg-navy-700'
                    }`}
                  />
                  <p className={`text-xs mt-1 text-center ${idx === currentStepIndex ? 'text-gold font-semibold' : 'text-gray-600'}`}>
                    {statusLabels[step]}
                  </p>
                </div>
                {idx < statusFlow.length - 1 && (
                  <div className={`w-3 h-3 rounded-full flex-shrink-0 ${idx < currentStepIndex ? 'bg-gold' : 'bg-navy-700'}`} />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Interaction timeline */}
        <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
          <h3 className="font-semibold text-white mb-4">Hermes Interaction Log</h3>
          {interactions.length === 0 ? (
            <p className="text-gray-500 text-sm">No interactions logged yet.</p>
          ) : (
            <div className="space-y-4 max-h-72 overflow-y-auto">
              {interactions.map((log, idx) => (
                <div key={idx} className="border-l-2 border-gold/30 pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-500 capitalize">{log.platform}</span>
                    <span className="text-gray-700">•</span>
                    <span className="text-xs text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <div className="bg-navy-900/50 rounded-lg p-3 mb-2">
                    <p className="text-xs text-gray-400 mb-1">Client</p>
                    <p className="text-gray-300 text-sm">"{log.message}"</p>
                  </div>
                  <div className="bg-gold/5 border border-gold/10 rounded-lg p-3">
                    <p className="text-xs text-gold mb-1">Hermes</p>
                    <p className="text-gray-300 text-sm">{log.hermesResponse}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Case notes */}
        <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
          <h3 className="font-semibold text-white mb-4">Case Notes</h3>

          <div className="mb-4">
            <textarea
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add a private note for this case..."
              className="w-full h-20 bg-navy-900 border border-gold/20 rounded-lg p-3 text-white placeholder-gray-600 focus:outline-none focus:border-gold resize-none text-sm"
            />
            <button
              onClick={addNote}
              disabled={!newNote.trim()}
              className="mt-2 px-4 py-2 bg-gold text-navy-900 font-semibold rounded-lg text-sm hover:bg-gold-light transition-colors disabled:opacity-40"
            >
              Add Note
            </button>
          </div>

          {caseData && (
            <div className="bg-navy-900/30 border border-gold/10 rounded-lg p-3 mb-4">
              <p className="text-xs text-gray-500 mb-1">Case #{caseData.id}</p>
              <p className="text-white text-sm">
                Value: <span className="text-gold font-bold">${caseData.value.toLocaleString()}</span>
              </p>
              <p className="text-gray-400 text-xs mt-1">
                Intake: {new Date(caseData.intakeDate).toLocaleDateString()}
                {caseData.closeDate && ` → Closed: ${new Date(caseData.closeDate).toLocaleDateString()}`}
              </p>
            </div>
          )}

          <div className="space-y-3 max-h-48 overflow-y-auto">
            {notes.length === 0 ? (
              <p className="text-gray-600 text-sm">No notes yet.</p>
            ) : (
              notes.map((note, idx) => (
                <div key={idx} className="bg-navy-900/50 border border-gold/10 rounded-lg p-3">
                  <p className="text-gray-400 text-xs mb-1">{new Date(note.timestamp).toLocaleString()}</p>
                  <p className="text-gray-300 text-sm">{note.text}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
