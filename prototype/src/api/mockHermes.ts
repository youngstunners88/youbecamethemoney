import type { Lead, Case, InteractionLog, Metrics, ServiceType, LeadStatus } from '../types';

const serviceTypes: ServiceType[] = [
  'Commercial Law',
  'UCC Discharge',
  'Securitization Review',
  'Trust Verification',
  'Secured Party Creditor',
  'Banking Law',
  'Corporate Structuring'
];

const statuses: LeadStatus[] = ['new', 'qualified', 'consulting', 'retained', 'closed-won', 'closed-lost'];

const sources: Array<'telegram' | 'whatsapp' | 'discord' | 'cli' | 'web'> = ['telegram', 'whatsapp', 'discord', 'cli', 'web'];

const firstNames = ['James', 'Maria', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Patricia', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah'];
const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson'];

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function generateLead(id: number, override?: Partial<Lead>): Lead {
  const firstName = randomItem(firstNames);
  const lastName = randomItem(lastNames);
  const status = randomItem(statuses);
  const serviceType = randomItem(serviceTypes);
  
  return {
    id: `lead_${id}`,
    source: randomItem(sources),
    name: `${firstName} ${lastName}`,
    phone: `+1 (${randomInt(200, 999)}) ${randomInt(100, 999)}-${randomInt(1000, 9999)}`,
    email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@email.com`,
    serviceType,
    urgencyScore: randomInt(1, 10),
    status,
    timestamp: new Date(Date.now() - randomInt(0, 7 * 24 * 60 * 60 * 1000)).toISOString(),
    message: `Inquiry about ${serviceType.toLowerCase()} services. Need urgent assistance with ${randomInt(1, 5)} ${randomInt(1, 10) > 5 ? 'accounts' : 'properties'}.`,
    ...override
  };
}

// Generate 15 diverse mock leads
export const mockLeads: Lead[] = Array.from({ length: 15 }, (_, i) => generateLead(i + 1));

// Generate mock cases
export const mockCases: Case[] = mockLeads
  .filter(l => l.status === 'retained' || l.status === 'closed-won')
  .map((lead, idx) => ({
    id: `case_${idx + 1}`,
    leadId: lead.id,
    serviceType: lead.serviceType,
    value: randomInt(2500, 25000),
    intakeDate: lead.timestamp,
    closeDate: lead.status === 'closed-won' ? new Date(Date.now() - randomInt(0, 30 * 24 * 60 * 60 * 1000)).toISOString() : undefined,
    outcome: lead.status === 'closed-won' ? 'won' : 'pending'
  }));

// Generate mock interaction logs
export const mockInteractions: InteractionLog[] = mockLeads.slice(0, 8).map((lead) => ({
  timestamp: new Date(Date.now() - randomInt(0, 48 * 60 * 60 * 1000)).toISOString(),
  platform: lead.source,
  message: lead.message || 'Initial inquiry',
  hermesResponse: `Thank you for reaching out about ${lead.serviceType}. I've noted your urgency level (${lead.urgencyScore}/10). Daniel Garcia will review your case within 24 hours. Please provide any relevant documentation.`,
  leadId: lead.id
}));

// Calculate mock metrics
export const mockMetrics: Metrics = {
  totalLeads: mockLeads.length,
  conversionRate: Math.round((mockCases.length / mockLeads.length) * 100),
  avgCaseValue: Math.round(mockCases.reduce((sum, c) => sum + c.value, 0) / (mockCases.length || 1)),
  avgIntakeToConsultDays: randomInt(2, 7),
  pipelineValue: mockLeads
    .filter(l => ['new', 'qualified', 'consulting'].includes(l.status))
    .reduce((sum, l) => sum + (l.urgencyScore * 1000), 0),
  leadsByStatus: {
    new: mockLeads.filter(l => l.status === 'new').length,
    qualified: mockLeads.filter(l => l.status === 'qualified').length,
    consulting: mockLeads.filter(l => l.status === 'consulting').length,
    retained: mockLeads.filter(l => l.status === 'retained').length,
    'closed-won': mockLeads.filter(l => l.status === 'closed-won').length,
    'closed-lost': mockLeads.filter(l => l.status === 'closed-lost').length,
  }
};

// Simulate real-time lead generation
export function simulateNewLead(): Lead {
  const newLead = generateLead(mockLeads.length + 1, {
    status: 'new',
    timestamp: new Date().toISOString()
  });
  mockLeads.unshift(newLead);
  mockMetrics.totalLeads++;
  mockMetrics.leadsByStatus.new++;
  return newLead;
}

// Mock API functions
export const mockHermesAPI = {
  getLeads: () => Promise.resolve([...mockLeads]),
  getCases: () => Promise.resolve([...mockCases]),
  getInteractions: () => Promise.resolve([...mockInteractions]),
  getMetrics: () => Promise.resolve({ ...mockMetrics }),
  updateLeadStatus: (leadId: string, status: LeadStatus) => {
    const lead = mockLeads.find(l => l.id === leadId);
    if (lead) {
      mockMetrics.leadsByStatus[lead.status]--;
      lead.status = status;
      mockMetrics.leadsByStatus[status]++;
    }
    return Promise.resolve(lead);
  },
  sendVoiceCommand: (command: string) => {
    return Promise.resolve({
      response: `Hermes received: "${command}". Processing your request...`,
      action: 'Processing',
      timestamp: new Date().toISOString()
    });
  }
};
