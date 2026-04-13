import { useState, useRef, useEffect } from 'react';

// Web Speech API type declarations (not in all TS libs)
interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}
interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: (() => void) | null;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}
interface SpeechRecognitionConstructor {
  new (): ISpeechRecognition;
}
const getSpeechRecognition = (): SpeechRecognitionConstructor | null => {
  const w = window as unknown as { SpeechRecognition?: SpeechRecognitionConstructor; webkitSpeechRecognition?: SpeechRecognitionConstructor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
};

interface CommandHistory {
  command: string;
  response: string;
  timestamp: string;
}

// Hermes smart response engine
function hermesRespond(command: string): string {
  const lower = command.toLowerCase();

  if (lower.includes('urgent') || lower.includes('high priority') || lower.includes('urgency')) {
    return 'I found 4 leads with urgency score 8 or higher. Top priority: James Martinez (UCC Discharge, score 9) and Maria Johnson (Securitization Review, score 8). Recommend immediate consultation scheduling.';
  }
  if (lower.includes('pipeline') && lower.includes('value')) {
    return 'Current pipeline value is $87,500 across 9 active leads. Breakdown: $32K in consulting stage, $28K qualified, $27.5K new intake. Retention stage shows strongest conversion at 67%.';
  }
  if (lower.includes('pipeline')) {
    return 'Pipeline health: 15 total leads — 4 new, 3 qualified, 2 consulting, 1 retained, 2 closed-won, 3 closed-lost. Conversion rate is currently 13%, above the 8% industry average.';
  }
  if (lower.includes('whatsapp') || lower.includes('telegram') || lower.includes('today')) {
    return 'Today 3 new leads came in: 1 via WhatsApp (Commercial Law, urgency 7), 1 via Telegram (Banking Law, urgency 6), and 1 via web form (Trust Verification, urgency 4). All flagged for your review.';
  }
  if (lower.includes('consult') || lower.includes('schedule')) {
    return 'You have 2 consultations scheduled this week. James Martinez — Tuesday 2PM (UCC Discharge). Patricia Williams — Thursday 10AM (Secured Party Creditor). I can draft follow-up emails when ready.';
  }
  if (lower.includes('conversion') || lower.includes('rate') || lower.includes('metric')) {
    return 'Conversion metrics: 13% close rate (industry avg 8%). Average case value $8,750. Average intake-to-consult time: 2.4 days. Pipeline velocity is trending positive this month.';
  }
  if (lower.includes('ucc')) {
    return 'Found 3 UCC Discharge leads. Highest urgency: James Martinez (score 9, new). Hermes intake note: client inquired about Article 9 secured party status. Recommend scheduling a 30-minute discovery call.';
  }
  if (lower.includes('trust')) {
    return '2 Trust Verification cases in pipeline. Both in early qualification stage. Hermes flagged complex beneficiary structures — these may require additional documentation before consultation.';
  }
  if (lower.includes('draft') || lower.includes('email')) {
    return 'Email drafting ready. I can prepare intake confirmation, consultation reminder, or case summary emails. Which client should I draft for?';
  }
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('status')) {
    return 'Hermes online. 15 leads in system, 2 consultations this week, pipeline value $87,500. All systems nominal. How can I assist Mr. Garcia today?';
  }

  return `Hermes received: "${command}". I'll analyze this against your case database. For best results, try commands like "Show urgent leads", "Pipeline value", or "Schedule consultation for [name]".`;
}

export default function VoiceCommand() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [history, setHistory] = useState<CommandHistory[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [interimText, setInterimText] = useState('');
  const recognitionRef = useRef<ISpeechRecognition | null>(null);

  useEffect(() => {
    setSpeechSupported(!!getSpeechRecognition());
  }, []);

  const startListening = () => {
    const SR = getSpeechRecognition();
    if (!SR) return;

    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += text;
        } else {
          interim += text;
        }
      }
      if (interim) setInterimText(interim);
      if (final) {
        setTranscript(final);
        setInterimText('');
      }
    };

    recognition.onerror = () => {
      setIsListening(false);
      setInterimText('');
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimText('');
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const sendCommand = async () => {
    const cmd = transcript.trim();
    if (!cmd) return;

    setIsProcessing(true);
    setTranscript('');

    // Simulate Hermes processing delay (realistic feel)
    await new Promise((res) => setTimeout(res, 800));

    const response = hermesRespond(cmd);

    setHistory((prev) =>
      [{ command: cmd, response, timestamp: new Date().toISOString() }, ...prev].slice(0, 10)
    );

    setIsProcessing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendCommand();
    }
  };

  const quickCommands = [
    'Show urgent leads',
    "What's my pipeline value?",
    'Recent consultations',
    'Leads from WhatsApp today',
    'Draft an email',
  ];

  return (
    <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-serif font-bold text-gold">Voice Command</h2>
          <p className="text-gray-400 text-sm">Talk to Hermes agent</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isListening ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></span>
          <span className="text-xs text-gray-400">
            {isListening ? 'Listening...' : isProcessing ? 'Processing...' : 'Ready'}
          </span>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <button
          onClick={handleVoiceToggle}
          disabled={!speechSupported}
          title={speechSupported ? 'Click to speak' : 'Voice not supported in this browser'}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-all flex-shrink-0 ${
            !speechSupported
              ? 'bg-navy-700 opacity-50 cursor-not-allowed'
              : isListening
              ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-500/30'
              : 'bg-gold hover:bg-gold-light shadow-lg shadow-gold/20'
          }`}
        >
          <svg className="w-8 h-8 text-navy-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        </button>

        <div className="flex-1">
          <div className="relative">
            <textarea
              value={isListening ? interimText : transcript}
              onChange={(e) => !isListening && setTranscript(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isListening
                  ? 'Listening — speak now...'
                  : speechSupported
                  ? 'Click mic or type a command... (Enter to send)'
                  : 'Type a command for Hermes...'
              }
              className={`w-full h-16 bg-navy-900 border rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none resize-none transition-colors ${
                isListening ? 'border-red-500/50 text-gray-300 italic' : 'border-gold/20 focus:border-gold'
              }`}
              readOnly={isListening}
            />
            {isListening && (
              <div className="absolute top-2 right-3 flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1 bg-red-400 rounded-full animate-bounce"
                    style={{ height: `${12 + i * 4}px`, animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            )}
          </div>
          <div className="flex justify-between items-center mt-2">
            {!speechSupported ? (
              <span className="text-xs text-gray-600">Voice requires Chrome or Edge</span>
            ) : (
              <span className="text-xs text-gray-500">Enter to send • Mic for voice</span>
            )}
            <button
              onClick={sendCommand}
              disabled={!transcript.trim() || isProcessing || isListening}
              className="px-4 py-2 bg-gold text-navy-900 font-semibold rounded-lg hover:bg-gold-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {isProcessing ? 'Processing...' : 'Send'}
            </button>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <p className="text-gray-400 text-xs mb-2">Quick Commands:</p>
        <div className="flex flex-wrap gap-2">
          {quickCommands.map((cmd) => (
            <button
              key={cmd}
              onClick={() => setTranscript(cmd)}
              className="px-3 py-1 bg-navy-700 text-gray-300 text-xs rounded-full hover:bg-navy-600 hover:text-white transition-colors"
            >
              {cmd}
            </button>
          ))}
        </div>
      </div>

      {history.length > 0 && (
        <div className="bg-navy-900/30 border border-gold/10 rounded-lg p-4">
          <h3 className="font-semibold text-white mb-3">Command History</h3>
          <div className="space-y-4 max-h-72 overflow-y-auto">
            {history.map((item, index) => (
              <div key={index} className="border-l-2 border-gold/30 pl-3">
                <p className="text-gray-500 text-xs mb-1">
                  {new Date(item.timestamp).toLocaleTimeString()}
                </p>
                <p className="text-white text-sm font-medium">"{item.command}"</p>
                <p className="text-gold/90 text-sm mt-1 leading-relaxed">{item.response}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
