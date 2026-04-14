import { useState, useRef, useEffect, useCallback } from 'react';
import type {
  InterviewAnswer,
  BehavioralMetadata,
  InterviewSubmission,
  InterviewAnalysisResponse,
} from '../types/interview';

// ── Constants ──────────────────────────────────────────────────────────────────

const INTERVIEW_API = 'http://localhost:8090/api/interview/submit';

const LEGAL_TERMS = [
  'ucc', 'article 3', 'discharge', 'securitization', 'trust', 'creditor',
  'debtor', 'negotiable instrument', 'promissory note', 'lien', 'jurisdiction',
  'litigation', 'settlement', 'breach', 'contract', 'indemnity', 'fiduciary',
  'beneficiary', 'trustee', 'secured party', 'remedy', 'allonge',
];

const HESITATION_MARKERS = [
  "i'm not sure", "i don't know", "maybe", "probably", "kind of",
  "sort of", "i think", "not really sure", "unclear", "not sure",
  "i guess", "possibly", "i'm unsure",
];

const CONFIDENCE_MARKERS = [
  "definitely", "absolutely", "clearly", "exactly", "specifically",
  "i need", "we require", "this is urgent", "immediately", "i have",
  "my documents show", "the amount is", "the jurisdiction is",
];

const QUESTIONS = [
  {
    id: 1, key: 'situation',
    question: "Describe your situation. What brought you here today?",
    type: 'text' as const,
    placeholder: "Tell us about your matter — be as specific as possible...",
    required: true,
  },
  {
    id: 2, key: 'matter_type',
    question: "What type of legal matter are you dealing with?",
    type: 'select' as const,
    options: [
      'UCC Discharge', 'Contract Dispute', 'Securitization Review',
      'Trust Verification', 'Debt Enforcement', 'Corporate Formation', 'Other',
    ],
    required: true,
  },
  {
    id: 3, key: 'amount',
    question: "What is the approximate amount at stake?",
    type: 'range' as const,
    options: [
      'Under $10,000', '$10,000–$50,000', '$50,000–$250,000',
      '$250,000–$1M', 'Over $1M', 'Not certain yet',
    ],
    required: true,
  },
  {
    id: 4, key: 'urgency',
    question: "How urgent is your matter?",
    type: 'select' as const,
    options: [
      'Immediate — action needed this week',
      'Within the month',
      'Within 3 months',
      'Exploratory — just researching',
    ],
    required: true,
  },
  {
    id: 5, key: 'jurisdiction',
    question: "What state or jurisdiction does this matter fall under?",
    type: 'text' as const,
    placeholder: "e.g., California, New York, Federal...",
    required: true,
  },
  {
    id: 6, key: 'prior_action',
    question: "Have you taken any prior legal action on this matter?",
    type: 'yesno' as const,
    options: ['Yes, I have', 'No, this would be my first step', 'There were proceedings I was not involved in'],
    required: true,
  },
  {
    id: 7, key: 'documentation',
    question: "Do you have documentation ready? (contracts, notices, correspondence)",
    type: 'yesno' as const,
    options: ['Yes — fully organized', 'Partial — some documents', 'Not yet — but I can gather them', 'No documentation exists'],
    required: true,
  },
  {
    id: 8, key: 'desired_outcome',
    question: "What is the outcome you are seeking?",
    type: 'text' as const,
    placeholder: "Describe what a successful resolution looks like for you...",
    required: true,
  },
];

// ── Behavioral scoring ─────────────────────────────────────────────────────────

function scoreBehavior(answers: InterviewAnswer[]): BehavioralMetadata {
  const textAnswers = answers.filter(a =>
    ['situation', 'jurisdiction', 'desired_outcome'].includes(a.key)
  );

  const fullText = textAnswers.map(a => a.value.toLowerCase()).join(' ');
  const wordCount = fullText.split(/\s+/).filter(Boolean).length;

  // Confidence: assertive language + word count (more words = more engaged)
  const confidenceMarkerHits = CONFIDENCE_MARKERS.filter(m => fullText.includes(m)).length;
  const tone_confidence = Math.min(100, 30 + confidenceMarkerHits * 12 + Math.min(wordCount * 0.8, 40));

  // Urgency: from structured answer + urgency language in text
  const urgencyAnswer = answers.find(a => a.key === 'urgency')?.value ?? '';
  const urgencyBase = urgencyAnswer.includes('Immediate') ? 90
    : urgencyAnswer.includes('month') ? 60
    : urgencyAnswer.includes('3 months') ? 35
    : 15;
  const urgency_score = Math.min(100, urgencyBase + (fullText.includes('urgent') ? 10 : 0));

  // Knowledge: legal term usage
  const termHits = LEGAL_TERMS.filter(t => fullText.includes(t)).length;
  const knowledge_level = Math.min(10, 1 + termHits * 1.5);

  // Hesitation: vague language
  const hesitationHits = HESITATION_MARKERS.filter(m => fullText.includes(m)).length;
  const avgEditCount = answers.reduce((s, a) => s + a.editCount, 0) / Math.max(answers.length, 1);
  const hesitation_score = Math.min(100, hesitationHits * 18 + avgEditCount * 5);

  const avgTime = answers.reduce((s, a) => s + a.timeSpentMs, 0) / Math.max(answers.length, 1);
  const totalEdits = answers.reduce((s, a) => s + a.editCount, 0);

  return {
    tone_confidence: Math.round(tone_confidence),
    urgency_score: Math.round(urgency_score),
    knowledge_level: Math.round(knowledge_level * 10) / 10,
    hesitation_score: Math.round(hesitation_score),
    avg_time_per_question_ms: Math.round(avgTime),
    total_edit_count: totalEdits,
  };
}

function buildTranscript(answers: InterviewAnswer[]): string {
  return answers
    .map((a, i) => {
      const q = QUESTIONS.find(q => q.key === a.key);
      return `Q${i + 1}: ${q?.question ?? a.key}\nA: ${a.value}`;
    })
    .join('\n\n');
}

// ── Mock API (used when real endpoint unreachable) ────────────────────────────

async function mockAnalyze(sub: InterviewSubmission): Promise<InterviewAnalysisResponse> {
  await new Promise(r => setTimeout(r, 1800)); // simulate network
  const delta = Math.round(
    (sub.metadata.tone_confidence - 50) * 0.3 +
    (sub.metadata.urgency_score - 50) * 0.2 +
    sub.metadata.knowledge_level * 1.5
  );
  const warmthBefore = 50;
  const warmthAfter = Math.min(100, Math.max(0, warmthBefore + delta));
  return {
    success: true,
    interview_id: `mock_${Date.now()}`,
    warmth_score_before: warmthBefore,
    warmth_score_after: warmthAfter,
    warmth_delta: delta,
    extracted_service: sub.answers.matter_type ?? 'Unknown',
    extracted_jurisdiction: sub.answers.jurisdiction ?? 'Unknown',
    behavior_profile: {
      tone_confidence: sub.metadata.tone_confidence,
      tone_urgency: sub.metadata.urgency_score,
      knowledge_level: Math.round(sub.metadata.knowledge_level),
      hesitation_score: sub.metadata.hesitation_score,
      stated_urgency: sub.answers.urgency?.includes('Immediate') ? 'immediate'
        : sub.answers.urgency?.includes('month') ? 'month' : 'exploratory',
      stated_amount: null,
      stated_jurisdiction: sub.answers.jurisdiction ?? null,
      key_signals: [
        sub.metadata.tone_confidence > 60 ? 'High confidence speaker' : 'Uncertain tone detected',
        sub.metadata.urgency_score > 70 ? 'Time-critical matter' : 'No immediate urgency',
        sub.metadata.knowledge_level > 5 ? 'Legally informed client' : 'General public knowledge',
      ],
      summary: `Client presents a ${sub.answers.matter_type?.toLowerCase() ?? 'legal'} matter in ${sub.answers.jurisdiction ?? 'unknown jurisdiction'} with ${sub.metadata.urgency_score > 70 ? 'high' : 'moderate'} urgency signals.`,
    },
  };
}

async function submitInterview(submission: InterviewSubmission): Promise<InterviewAnalysisResponse> {
  try {
    const res = await fetch(INTERVIEW_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(submission),
    });
    if (!res.ok) throw new Error(`API ${res.status}`);
    return res.json();
  } catch {
    console.warn('Interview API unreachable — using mock response');
    return mockAnalyze(submission);
  }
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function AvatarBubble({ text, isTyping }: { text: string; isTyping: boolean }) {
  return (
    <div className="flex gap-3 items-start">
      <div className="w-12 h-12 rounded-full border-2 border-gold/60 bg-navy-800 flex items-center justify-center flex-shrink-0 shadow-lg">
        <span className="text-xl">⚖️</span>
      </div>
      <div className="bg-navy-800 border border-gold/20 rounded-2xl rounded-tl-none px-4 py-3 max-w-lg text-sm leading-relaxed">
        {isTyping ? (
          <span className="flex gap-1 items-center h-5">
            {[0, 150, 300].map(d => (
              <span
                key={d}
                className="inline-block w-1.5 h-1.5 rounded-full bg-gold animate-pulse"
                style={{ animationDelay: `${d}ms` }}
              />
            ))}
          </span>
        ) : (
          <span className="text-gray-200">{text}</span>
        )}
      </div>
    </div>
  );
}

function ProgressDots({ total, current }: { total: number; current: number }) {
  return (
    <div className="flex gap-2 justify-center">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={`rounded-full transition-all duration-300 ${
            i < current
              ? 'w-2.5 h-2.5 bg-gold'
              : i === current
              ? 'w-3 h-3 bg-gold shadow-[0_0_8px_rgba(212,175,55,0.7)]'
              : 'w-2.5 h-2.5 bg-navy-700'
          }`}
        />
      ))}
    </div>
  );
}

function WarmthMeter({ before, after, delta }: { before: number; after: number; delta: number }) {
  const pct = (after / 100) * 100;
  const color = after >= 70 ? 'from-gold to-yellow-400' : after >= 40 ? 'from-orange-400 to-gold' : 'from-red-500 to-orange-500';
  const label = after >= 70 ? 'Hot Lead' : after >= 40 ? 'Warm Lead' : 'Cold Lead';
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-gray-400">
        <span>Warmth Score</span>
        <span className="text-gold font-semibold">{after}/100 — {label}</span>
      </div>
      <div className="h-2.5 rounded-full bg-navy-700 overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${color} transition-all duration-1000`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-xs">
        <span className="text-gray-500">Was: {before}</span>
        <span className={delta >= 0 ? 'text-green-400' : 'text-red-400'}>
          {delta >= 0 ? '+' : ''}{delta} delta
        </span>
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────

interface Props {
  leadId?: string;
}

type Phase = 'intro' | 'interview' | 'submitting' | 'result' | 'error';

export default function LemonsliceInterview({ leadId = '' }: Props) {
  const [phase, setPhase] = useState<Phase>('intro');
  const [currentQ, setCurrentQ] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [showQuestion, setShowQuestion] = useState(false);
  const [draft, setDraft] = useState('');
  const [editCount, setEditCount] = useState(0);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [answers, setAnswers] = useState<InterviewAnswer[]>([]);
  const [result, setResult] = useState<InterviewAnalysisResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const q = QUESTIONS[currentQ];
  const isLast = currentQ === QUESTIONS.length - 1;

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [answers, showQuestion, phase]);

  // Animate in question when we advance
  const advanceQuestion = useCallback((nextIdx: number) => {
    setShowQuestion(false);
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setShowQuestion(true);
      setCurrentQ(nextIdx);
      setDraft('');
      setEditCount(0);
      setQuestionStartTime(Date.now());
    }, 900);
  }, []);

  const startInterview = () => {
    setPhase('interview');
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      setShowQuestion(true);
      setQuestionStartTime(Date.now());
    }, 1000);
  };

  const recordAnswer = (value: string) => {
    const spent = Date.now() - questionStartTime;
    const answer: InterviewAnswer = {
      questionId: q.id,
      key: q.key,
      value,
      timeSpentMs: spent,
      editCount,
    };
    const updated = [...answers, answer];
    setAnswers(updated);

    if (isLast) {
      handleSubmit(updated);
    } else {
      advanceQuestion(currentQ + 1);
    }
  };

  const handleSubmit = async (finalAnswers: InterviewAnswer[]) => {
    setPhase('submitting');
    const metadata = scoreBehavior(finalAnswers);
    const transcript = buildTranscript(finalAnswers);
    const submission: InterviewSubmission = {
      lead_id: leadId || `web_${Date.now()}`,
      session_id: `session_${Date.now()}`,
      answers: Object.fromEntries(finalAnswers.map(a => [a.key, a.value])),
      transcript,
      metadata,
      submitted_at: new Date().toISOString(),
    };

    // Log to console for testing
    console.group('[LemonsliceInterview] Submission payload');
    console.log(JSON.stringify(submission, null, 2));
    console.groupEnd();

    try {
      const res = await submitInterview(submission);
      setResult(res);
      setPhase('result');
    } catch (err) {
      setErrorMsg(String(err));
      setPhase('error');
    }
  };

  // ── Render helpers ─────────────────────────────────────────────────────────

  const renderInput = () => {
    if (!showQuestion) return null;

    if (q.type === 'text') {
      return (
        <div className="flex flex-col gap-3 animate-fade-up">
          <textarea
            rows={4}
            value={draft}
            placeholder={q.placeholder ?? ''}
            onChange={e => { setDraft(e.target.value); setEditCount(c => c + 1); }}
            className="w-full bg-navy-800 border border-navy-600 focus:border-gold rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-500 outline-none resize-none transition-colors"
          />
          <button
            disabled={draft.trim().length < 3}
            onClick={() => recordAnswer(draft.trim())}
            className="self-end px-6 py-2.5 rounded-xl bg-gold text-navy-900 font-bold text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 transition-all"
          >
            {isLast ? 'Submit Interview →' : 'Continue →'}
          </button>
        </div>
      );
    }

    if (q.type === 'select' || q.type === 'range' || q.type === 'yesno') {
      return (
        <div className="flex flex-col gap-2 animate-fade-up">
          {q.options?.map(opt => (
            <button
              key={opt}
              onClick={() => recordAnswer(opt)}
              className="text-left px-4 py-3 rounded-xl border border-navy-600 hover:border-gold hover:bg-gold/5 text-sm text-gray-200 transition-all"
            >
              {opt}
            </button>
          ))}
        </div>
      );
    }

    return null;
  };

  // ── Phases ─────────────────────────────────────────────────────────────────

  if (phase === 'intro') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4 py-12 gap-8 max-w-xl mx-auto">
        <div className="w-20 h-20 rounded-full border-2 border-gold bg-navy-800 flex items-center justify-center shadow-[0_0_24px_rgba(212,175,55,0.2)]">
          <span className="text-4xl">⚖️</span>
        </div>
        <div>
          <h2 className="font-serif text-2xl font-bold text-gold mb-2">Client Intake Interview</h2>
          <p className="text-gray-400 text-sm leading-relaxed">
            This 8-question interview takes about 4 minutes. Your answers help us
            understand your situation before we speak, so your consultation time
            is focused entirely on your matter.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-4 text-center text-xs text-gray-500 w-full">
          {[['4 min', 'Average time'], ['8', 'Questions'], ['100%', 'Confidential']].map(([val, lbl]) => (
            <div key={lbl} className="bg-navy-800 rounded-xl p-3 border border-navy-700">
              <div className="text-gold font-bold text-lg">{val}</div>
              <div>{lbl}</div>
            </div>
          ))}
        </div>
        <button
          onClick={startInterview}
          className="px-8 py-3 rounded-xl bg-gold text-navy-900 font-bold hover:brightness-110 transition-all text-sm shadow-lg"
        >
          Begin Interview →
        </button>
      </div>
    );
  }

  if (phase === 'submitting') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 text-center">
        <div className="w-16 h-16 rounded-full border-2 border-gold animate-spin border-t-transparent" />
        <div>
          <p className="text-gold font-semibold text-lg">Analyzing your responses…</p>
          <p className="text-gray-400 text-sm mt-1">Extracting behavioral profile and warmth score</p>
        </div>
      </div>
    );
  }

  if (phase === 'error') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center px-4">
        <span className="text-4xl">⚠️</span>
        <p className="text-red-400 font-semibold">Submission failed</p>
        <p className="text-gray-500 text-sm">{errorMsg}</p>
        <button
          onClick={() => { setPhase('interview'); setAnswers([]); setCurrentQ(0); setShowQuestion(false); }}
          className="px-6 py-2 rounded-xl border border-gold/40 text-gold text-sm hover:bg-gold/5 transition-all"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (phase === 'result' && result) {
    const p = result.behavior_profile;
    return (
      <div className="max-w-2xl mx-auto py-8 px-4 space-y-6">
        <div className="text-center space-y-2">
          <div className="text-3xl">✅</div>
          <h2 className="font-serif text-xl font-bold text-gold">Interview Complete</h2>
          <p className="text-gray-400 text-sm">
            Our team will reach out within 2 hours to schedule your consultation.
          </p>
        </div>

        <div className="bg-navy-800 border border-gold/20 rounded-2xl p-5 space-y-4">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Your Profile</div>
          <WarmthMeter before={result.warmth_score_before} after={result.warmth_score_after} delta={result.warmth_delta} />

          <div className="grid grid-cols-2 gap-3 text-sm">
            {[
              ['Matter Type', result.extracted_service],
              ['Jurisdiction', result.extracted_jurisdiction],
              ['Confidence', `${p.tone_confidence}/100`],
              ['Knowledge Level', `${p.knowledge_level}/10`],
            ].map(([label, val]) => (
              <div key={label} className="bg-navy-900 rounded-xl p-3 border border-navy-700">
                <div className="text-xs text-gray-500 mb-1">{label}</div>
                <div className="text-gold font-semibold">{val}</div>
              </div>
            ))}
          </div>

          {p.key_signals.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-2">Key Signals</div>
              <ul className="space-y-1">
                {p.key_signals.map(sig => (
                  <li key={sig} className="flex gap-2 text-sm text-gray-300">
                    <span className="text-gold">•</span>{sig}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {p.summary && (
            <div className="bg-navy-900 rounded-xl p-3 border border-navy-700 text-sm text-gray-300 leading-relaxed italic">
              "{p.summary}"
            </div>
          )}
        </div>

        <p className="text-center text-xs text-gray-600">
          Interview ID: {result.interview_id}
        </p>
      </div>
    );
  }

  // ── Interview phase ────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto py-6 px-4 flex flex-col gap-6">
      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-gray-500">
          <span>Question {currentQ + 1} of {QUESTIONS.length}</span>
          <span>{Math.round(((currentQ) / QUESTIONS.length) * 100)}% complete</span>
        </div>
        <ProgressDots total={QUESTIONS.length} current={currentQ} />
      </div>

      {/* Chat history */}
      <div className="flex flex-col gap-5">
        {/* Previous Q&A */}
        {answers.map((ans, _i) => {
          const prevQ = QUESTIONS.find(q => q.key === ans.key);
          return (
            <div key={ans.questionId} className="flex flex-col gap-2 opacity-60">
              <AvatarBubble text={prevQ?.question ?? ''} isTyping={false} />
              <div className="ml-14 bg-gold/10 border border-gold/20 rounded-2xl rounded-tr-none px-4 py-2 text-sm text-gray-200 self-end max-w-sm">
                {ans.value}
              </div>
            </div>
          );
        })}

        {/* Current question */}
        {phase === 'interview' && (
          <div className="flex flex-col gap-4">
            <AvatarBubble text={isTyping ? '' : (showQuestion ? q.question : '')} isTyping={isTyping} />
            {showQuestion && renderInput()}
          </div>
        )}

        <div ref={chatEndRef} />
      </div>
    </div>
  );
}
