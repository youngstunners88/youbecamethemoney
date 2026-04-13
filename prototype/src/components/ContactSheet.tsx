import { useState } from 'react';
import type { Lead } from '../types';

interface Contact {
  id: string;
  name: string;
  phone: string;
  email: string;
  lastContact: string;
  status: 'hot' | 'warm' | 'luke' | 'cold';
  serviceType: string;
}

interface ContactSheetProps {
  leads: Lead[];
}

const tempColors = {
  hot: 'bg-red-600 text-white',
  warm: 'bg-orange-500 text-white',
  luke: 'bg-blue-400 text-white',
  cold: 'bg-gray-600 text-white'
};

export default function ContactSheet({ leads }: ContactSheetProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Convert leads to contacts format
  const contacts: Contact[] = leads
    .filter(lead => lead.phone && lead.email)
    .map(lead => ({
      id: lead.id,
      name: lead.name,
      phone: lead.phone || 'N/A',
      email: lead.email || 'N/A',
      lastContact: new Date(lead.timestamp).toLocaleDateString(),
      status: (lead.urgencyScore >= 8 ? 'hot' :
               lead.urgencyScore >= 6 ? 'warm' :
               lead.urgencyScore >= 4 ? 'luke' : 'cold') as any,
      serviceType: lead.serviceType
    }))
    .filter(contact =>
      contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.phone.includes(searchTerm) ||
      contact.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

  const handleCopyContact = (phone: string, email: string) => {
    const text = `${phone} | ${email}`;
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="bg-navy-800 border-t border-gold/20 px-6 py-4">
      {/* Minimized View */}
      {!showDetails && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-gold font-semibold text-sm">📋 CONTACT SHEET</span>
            <span className="text-gray-400 text-sm">{contacts.length} active contacts</span>
            <div className="flex gap-2">
              {contacts.slice(0, 3).map((contact) => (
                <button
                  key={contact.id}
                  className="px-2 py-1 bg-navy-700 hover:bg-navy-600 rounded text-xs text-gray-300"
                  onClick={() => handleCopyContact(contact.phone, contact.email)}
                  title={`${contact.name}: ${contact.phone}`}
                >
                  {contact.name.split(' ')[0]}
                </button>
              ))}
              {contacts.length > 3 && (
                <span className="px-2 py-1 text-xs text-gray-500">+{contacts.length - 3} more</span>
              )}
            </div>
          </div>
          <button
            onClick={() => setShowDetails(true)}
            className="px-4 py-2 bg-gold/20 hover:bg-gold/30 text-gold rounded-lg text-sm transition-colors"
          >
            View Details →
          </button>
        </div>
      )}

      {/* Expanded View */}
      {showDetails && (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gold font-semibold text-lg">📋 Contact Management</h3>
            <button
              onClick={() => setShowDetails(false)}
              className="text-gray-400 hover:text-white text-xl"
            >
              ✕
            </button>
          </div>

          {/* Search */}
          <input
            type="text"
            placeholder="Search by name, phone, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-navy-700 border border-gold/30 text-white px-4 py-2 rounded-lg focus:outline-none focus:border-gold"
          />

          {/* Table */}
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-navy-900">
                <tr className="border-b border-gold/20">
                  <th className="text-left px-4 py-2 text-gold">Name</th>
                  <th className="text-left px-4 py-2 text-gold">Phone</th>
                  <th className="text-left px-4 py-2 text-gold">Email</th>
                  <th className="text-left px-4 py-2 text-gold">Service</th>
                  <th className="text-left px-4 py-2 text-gold">Status</th>
                  <th className="text-left px-4 py-2 text-gold">Last Contact</th>
                  <th className="text-left px-4 py-2 text-gold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gold/10">
                {contacts.map((contact) => (
                  <tr key={contact.id} className="hover:bg-navy-700/50">
                    <td className="px-4 py-3 text-white">{contact.name}</td>
                    <td className="px-4 py-3 text-gray-300 font-mono text-xs">{contact.phone}</td>
                    <td className="px-4 py-3 text-gray-300 font-mono text-xs">{contact.email}</td>
                    <td className="px-4 py-3 text-gray-400">{contact.serviceType}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${tempColors[contact.status]}`}>
                        {contact.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400">{contact.lastContact}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleCopyContact(contact.phone, contact.email)}
                        className="text-gold hover:text-gold-light text-xs"
                        title="Copy contact"
                      >
                        📋 Copy
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {contacts.length === 0 && (
            <div className="text-center py-8 text-gray-400">
              No contacts found matching "{searchTerm}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}
