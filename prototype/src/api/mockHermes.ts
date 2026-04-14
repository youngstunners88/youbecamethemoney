import type { Lead, Case, InteractionLog, Metrics, ServiceType, LeadStatus } from '../types';
export type { ServiceType, LeadStatus };

// ── Extended mock data types ───────────────────────────────────────────────────

export interface GrowthWeek {
  week: number;
  label: string;
  closeRate: number;
  warmthAvg: number;
  callsPerWeek: number;
  revenue: number;
}

export interface EconomicsData {
  currentCloseRate: number;
  projectedCloseRate: number;
  weeklyApiCost: number;
  revenueAddedPerWeek: number;
  roiMultiple: number;
  costPerLead: number;
  leadsPerWeek: number;
  avgCaseValue: number;
}

export interface HallOfFameProfile {
  id: string;
  headline: string;
  testimonial: string;
  service_type: string;
  jurisdiction: string;
  case_value: number;
  case_outcome: 'won' | 'settled' | 'referred';
  confidence_score: number;
  key_signals: string[];
  created_at: string;
}

export interface WarmthLead {
  id: string;
  name: string;
  serviceType: ServiceType;
  warmthScore: number;
  warmthTier: 'hot' | 'warm' | 'cold';
  urgencyScore: number;
  status: LeadStatus;
  timestamp: string;
  jurisdiction?: string;
  behaviorSummary?: string;
}

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

// ── Mock growth data (8-week Layer 3 trajectory) ──────────────────────────────

const GROWTH_DATA: GrowthWeek[] = [
  { week: 1, label: 'Week 1', closeRate: 18.5, warmthAvg: 52, callsPerWeek: 147, revenue: 8700 },
  { week: 2, label: 'Week 2', closeRate: 21.2, warmthAvg: 56, callsPerWeek: 147, revenue: 10000 },
  { week: 3, label: 'Week 3', closeRate: 24.1, warmthAvg: 61, callsPerWeek: 147, revenue: 11400 },
  { week: 4, label: 'Week 4', closeRate: 26.8, warmthAvg: 65, callsPerWeek: 147, revenue: 12700 },
  { week: 5, label: 'Week 5', closeRate: 28.3, warmthAvg: 68, callsPerWeek: 147, revenue: 13400 },
  { week: 6, label: 'Week 6', closeRate: 30.5, warmthAvg: 71, callsPerWeek: 147, revenue: 14400 },
  { week: 7, label: 'Week 7', closeRate: 32.8, warmthAvg: 74, callsPerWeek: 147, revenue: 15500 },
  { week: 8, label: 'Week 8', closeRate: 35.2, warmthAvg: 78, callsPerWeek: 147, revenue: 16600 },
];

const ECONOMICS: EconomicsData = {
  currentCloseRate: 18.5,
  projectedCloseRate: 35.2,
  weeklyApiCost: 0.001,
  revenueAddedPerWeek: 7900,
  roiMultiple: 7_900_000,
  costPerLead: 4.50,
  leadsPerWeek: 147,
  avgCaseValue: 3200,
};

const HOF_PROFILES: HallOfFameProfile[] = [
  {
    id: 'hof-001',
    headline: '$97,000 UCC Article 3 Enforcement — Won',
    testimonial:
      'Our client successfully enforced a $97,000 promissory note in California under UCC Article 3. ' +
      'From the first consultation, the team understood the urgency and moved decisively. ' +
      'The outcome exceeded all expectations.',
    service_type: 'UCC Discharge',
    jurisdiction: 'California',
    case_value: 97_000,
    case_outcome: 'won',
    confidence_score: 91,
    key_signals: ['Time-critical matter', 'High confidence speaker', 'Legally informed client'],
    created_at: new Date(Date.now() - 14 * 864e5).toISOString(),
  },
  {
    id: 'hof-002',
    headline: '$250,000 Securitization Review — Settled',
    testimonial:
      'A complex securitization dispute in New York was resolved through a structured settlement, ' +
      'recovering $250,000 for our client. The behavioral profile flagged urgency from the first interview, ' +
      'allowing Margarita to prioritize appropriately.',
    service_type: 'Securitization Review',
    jurisdiction: 'New York',
    case_value: 250_000,
    case_outcome: 'settled',
    confidence_score: 84,
    key_signals: ['Prior legal knowledge', 'Time-sensitive situation', 'Clear documentation'],
    created_at: new Date(Date.now() - 7 * 864e5).toISOString(),
  },
  {
    id: 'hof-003',
    headline: '$45,000 Trust Verification — Won',
    testimonial:
      'Trust verification proceedings in Texas concluded in our client\'s favor, ' +
      'confirming beneficiary rights on a $45,000 estate matter. The interview process identified ' +
      'key documents before the first call, saving significant time.',
    service_type: 'Trust Verification',
    jurisdiction: 'Texas',
    case_value: 45_000,
    case_outcome: 'won',
    confidence_score: 78,
    key_signals: ['High confidence speaker', 'Documentation ready', 'Legally informed client'],
    created_at: new Date(Date.now() - 3 * 864e5).toISOString(),
  },
];

const WARMTH_LEADS: WarmthLead[] = [
  {
    id: 'wl-001', name: 'Marcus Chen', serviceType: 'UCC Discharge',
    warmthScore: 87, warmthTier: 'hot', urgencyScore: 9, status: 'qualified',
    timestamp: new Date(Date.now() - 2 * 3600e3).toISOString(),
    jurisdiction: 'California',
    behaviorSummary: 'High confidence, immediate urgency, UCC knowledge, docs ready.',
  },
  {
    id: 'wl-002', name: 'Patricia Williams', serviceType: 'Securitization Review',
    warmthScore: 78, warmthTier: 'hot', urgencyScore: 8, status: 'new',
    timestamp: new Date(Date.now() - 4 * 3600e3).toISOString(),
    jurisdiction: 'New York',
    behaviorSummary: 'Clear situation, time-sensitive, prior legal experience.',
  },
  {
    id: 'wl-003', name: 'James Thompson', serviceType: 'Trust Verification',
    warmthScore: 61, warmthTier: 'warm', urgencyScore: 6, status: 'consulting',
    timestamp: new Date(Date.now() - 8 * 3600e3).toISOString(),
    jurisdiction: 'Texas',
    behaviorSummary: 'Moderate urgency, some legal knowledge, partial documentation.',
  },
  {
    id: 'wl-004', name: 'Sarah Martinez', serviceType: 'Commercial Law',
    warmthScore: 55, warmthTier: 'warm', urgencyScore: 5, status: 'new',
    timestamp: new Date(Date.now() - 12 * 3600e3).toISOString(),
    jurisdiction: 'Florida',
    behaviorSummary: 'Exploring options, timeline within the month.',
  },
  {
    id: 'wl-005', name: 'Robert Davis', serviceType: 'Banking Law',
    warmthScore: 32, warmthTier: 'cold', urgencyScore: 3, status: 'new',
    timestamp: new Date(Date.now() - 24 * 3600e3).toISOString(),
    jurisdiction: 'Illinois',
    behaviorSummary: 'Exploratory inquiry, high hesitation, no documentation.',
  },
  {
    id: 'wl-006', name: 'Linda Garcia', serviceType: 'Corporate Structuring',
    warmthScore: 28, warmthTier: 'cold', urgencyScore: 2, status: 'new',
    timestamp: new Date(Date.now() - 36 * 3600e3).toISOString(),
    jurisdiction: 'Georgia',
    behaviorSummary: 'Early research stage, no urgency signals detected.',
  },
];

// ── Mock API functions ─────────────────────────────────────────────────────────

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
  },
  getGrowthData: () => Promise.resolve([...GROWTH_DATA]),
  getEconomics: () => Promise.resolve({ ...ECONOMICS }),
  getHallOfFame: () => Promise.resolve([...HOF_PROFILES]),
  getWarmthLeads: () => Promise.resolve([...WARMTH_LEADS]),
};
