// Interview portal types

export interface InterviewQuestion {
  id: number;
  key: string;
  question: string;
  type: 'text' | 'select' | 'range' | 'yesno';
  options?: string[];
  placeholder?: string;
  required: boolean;
}

export interface InterviewAnswer {
  questionId: number;
  key: string;
  value: string;
  timeSpentMs: number; // behavioral: time to answer
  editCount: number;   // behavioral: how many times they edited
}

export interface BehavioralMetadata {
  tone_confidence: number;   // 0–100
  urgency_score: number;     // 0–100
  knowledge_level: number;   // 1–10
  hesitation_score: number;  // 0–100 (higher = more hesitant)
  avg_time_per_question_ms: number;
  total_edit_count: number;
}

export interface InterviewSubmission {
  lead_id: string;
  session_id: string;
  answers: Record<string, string>;
  transcript: string;       // formatted Q&A text for analyzer
  metadata: BehavioralMetadata;
  submitted_at: string;
}

export interface InterviewAnalysisResponse {
  success: boolean;
  interview_id: string;
  warmth_score_before: number;
  warmth_score_after: number;
  warmth_delta: number;
  extracted_service: string;
  extracted_jurisdiction: string;
  behavior_profile: {
    tone_confidence: number;
    tone_urgency: number;
    knowledge_level: number;
    hesitation_score: number;
    stated_urgency: string;
    stated_amount: number | null;
    stated_jurisdiction: string | null;
    key_signals: string[];
    summary: string;
  };
  error?: string;
}
