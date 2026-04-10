export interface Lead {
  id: string;
  source: 'telegram' | 'whatsapp' | 'discord' | 'cli' | 'web';
  name: string;
  phone?: string;
  email?: string;
  serviceType: ServiceType;
  urgencyScore: number;
  status: LeadStatus;
  timestamp: string;
  message?: string;
}

export type ServiceType = 
  | 'Commercial Law'
  | 'UCC Discharge'
  | 'Securitization Review'
  | 'Trust Verification'
  | 'Secured Party Creditor'
  | 'Banking Law'
  | 'Corporate Structuring';

export type LeadStatus = 
  | 'new'
  | 'qualified'
  | 'consulting'
  | 'retained'
  | 'closed-won'
  | 'closed-lost';

export interface Case {
  id: string;
  leadId: string;
  serviceType: ServiceType;
  value: number;
  intakeDate: string;
  closeDate?: string;
  outcome?: 'won' | 'lost' | 'pending';
}

export interface InteractionLog {
  timestamp: string;
  platform: string;
  message: string;
  hermesResponse: string;
  leadId: string;
}

export interface Metrics {
  totalLeads: number;
  conversionRate: number;
  avgCaseValue: number;
  avgIntakeToConsultDays: number;
  pipelineValue: number;
  leadsByStatus: Record<LeadStatus, number>;
}
