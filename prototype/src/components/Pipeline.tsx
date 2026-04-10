import { useState, useEffect } from 'react';
import type { Lead, LeadStatus } from '../types';
import { mockHermesAPI } from '../api/mockHermes';

const columns: { id: LeadStatus; label: string; color: string }[] = [
  { id: 'new', label: 'New', color: 'bg-blue-500/20 border-blue-500/30' },
  { id: 'qualified', label: 'Qualified', color: 'bg-yellow-500/20 border-yellow-500/30' },
  { id: 'consulting', label: 'Consulting', color: 'bg-orange-500/20 border-orange-500/30' },
  { id: 'retained', label: 'Retained', color: 'bg-green-500/20 border-green-500/30' },
  { id: 'closed-won', label: 'Closed Won', color: 'bg-emerald-500/20 border-emerald-500/30' },
  { id: 'closed-lost', label: 'Closed Lost', color: 'bg-red-500/20 border-red-500/30' },
];

export default function Pipeline() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [draggedLead, setDraggedLead] = useState<Lead | null>(null);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    const data = await mockHermesAPI.getLeads();
    setLeads(data);
  };

  const handleDragStart = (lead: Lead) => {
    setDraggedLead(lead);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent, status: LeadStatus) => {
    e.preventDefault();
    if (draggedLead && draggedLead.status !== status) {
      await mockHermesAPI.updateLeadStatus(draggedLead.id, status);
      setLeads(prev => prev.map(l => 
        l.id === draggedLead.id ? { ...l, status } : l
      ));
      setDraggedLead(null);
    }
  };

  const getLeadsByStatus = (status: LeadStatus) => {
    return leads.filter(lead => lead.status === status);
  };

  return (
    <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-serif font-bold text-gold">Pipeline</h2>
          <p className="text-gray-400 text-sm">Drag leads to update status</p>
        </div>
        <div className="flex gap-4 text-sm">
          <div className="text-gray-400">
            Total Value: <span className="text-gold font-bold">
              ${leads.reduce((sum, l) => sum + (l.urgencyScore * 1000), 0).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-3 overflow-x-auto">
        {columns.map((column) => {
          const columnLeads = getLeadsByStatus(column.id);
          return (
            <div
              key={column.id}
              className={`${column.color} border rounded-lg p-3 min-h-[400px]`}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, column.id)}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white text-sm">{column.label}</h3>
                <span className="bg-navy-900 text-white text-xs px-2 py-1 rounded-full">
                  {columnLeads.length}
                </span>
              </div>

              <div className="space-y-2">
                {columnLeads.map((lead) => (
                  <div
                    key={lead.id}
                    draggable
                    onDragStart={() => handleDragStart(lead)}
                    className="bg-navy-900/80 border border-gold/10 rounded-lg p-3 cursor-move hover:border-gold/30 transition-all"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-white text-sm truncate">
                        {lead.name}
                      </span>
                      <span className="text-xs text-gold font-bold">
                        {lead.urgencyScore}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mb-2 truncate">
                      {lead.serviceType}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className="capitalize">{lead.source}</span>
                      <span>•</span>
                      <span>${(lead.urgencyScore * 1000).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
