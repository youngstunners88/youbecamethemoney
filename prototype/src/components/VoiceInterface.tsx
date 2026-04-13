import { useState, useRef } from 'react';

interface VoiceCommand {
  command: string;
  response: string;
  timestamp: Date;
}

export default function VoiceInterface() {
  const [isListening, setIsListening] = useState(false);
  const [commands, setCommands] = useState<VoiceCommand[]>([]);
  const [audioLevel, setAudioLevel] = useState(0);
  const recognitionRef = useRef<any>(null);

  const startListening = () => {
    if (!recognitionRef.current) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onstart = () => setIsListening(true);
      recognitionRef.current.onend = () => setIsListening(false);

      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            processVoiceCommand(transcript);
          } else {
            interimTranscript += transcript;
          }
        }
      };
    }

    recognitionRef.current.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const processVoiceCommand = (transcript: string) => {
    const command = transcript.toLowerCase();
    let response = 'Command not recognized';

    if (command.includes('hot leads')) {
      response = 'Displaying hot leads. You have 5 prospects ready to close.';
    } else if (command.includes('call status')) {
      response = 'Mragerita completed 24 calls today with 89% success rate.';
    } else if (command.includes('revenue')) {
      response = 'Monthly revenue is 47,320 dollars, up 23 percent.';
    } else if (command.includes('roi')) {
      response = 'Return on investment is 460 percent.';
    } else if (command.includes('instagram')) {
      response = 'Instagram has 8,234 followers with 12.5 percent engagement rate.';
    } else if (command.includes('hermes status')) {
      response = 'Hermes is online and operating at 84 percent efficiency.';
    } else if (command.includes('schedule call')) {
      response = 'Initiating consultation call scheduler.';
    }

    const newCommand: VoiceCommand = {
      command: transcript,
      response,
      timestamp: new Date()
    };

    setCommands(prev => [newCommand, ...prev]);

    // Speak the response
    const utterance = new SpeechSynthesisUtterance(response);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="bg-navy-800 border border-gold/20 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-gold font-semibold text-lg">🎤 Voice Command Center</h3>
        <div className="flex items-center gap-4">
          {isListening && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
              <span className="text-red-500 text-sm font-semibold">Listening...</span>
            </div>
          )}
          <button
            onClick={isListening ? stopListening : startListening}
            className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
              isListening
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gold hover:bg-gold-light text-navy-900'
            }`}
          >
            {isListening ? '⏹️ Stop' : '🎙️ Start Listening'}
          </button>
        </div>
      </div>

      {/* Audio Waveform */}
      {isListening && (
        <div className="mb-6 p-4 bg-navy-700 rounded-lg">
          <div className="flex items-end justify-center gap-1 h-16">
            {[...Array(40)].map((_, i) => (
              <div
                key={i}
                className="w-1 bg-gradient-to-t from-gold to-gold-light rounded-full transition-all"
                style={{
                  height: `${Math.sin(i * 0.3 + Date.now() / 100) * 30 + 40}%`,
                  opacity: 0.8
                }}
              ></div>
            ))}
          </div>
          <p className="text-gray-400 text-sm text-center mt-2">Speak clearly for best results</p>
        </div>
      )}

      {/* Voice Command History */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {commands.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>🎤 No voice commands yet</p>
            <p className="text-sm mt-2">Try: "Show hot leads" or "What's the ROI?"</p>
          </div>
        ) : (
          commands.map((cmd, i) => (
            <div key={i} className="bg-navy-700 rounded-lg p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-gold font-semibold text-sm">You said:</p>
                  <p className="text-white">{cmd.command}</p>
                </div>
                <span className="text-xs text-gray-500">{cmd.timestamp.toLocaleTimeString()}</span>
              </div>
              <div className="border-l-2 border-gold/30 pl-4 py-2">
                <p className="text-gray-300 text-sm">🤖 Response:</p>
                <p className="text-emerald-400">{cmd.response}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Voice Command Examples */}
      <div className="mt-6 bg-gold/5 border border-gold/20 rounded-lg p-4">
        <p className="text-gold font-semibold text-sm mb-3">💡 Try These Voice Commands:</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-300">
          <button onClick={() => processVoiceCommand('Show hot leads')} className="text-left hover:text-gold">
            • "Show hot leads"
          </button>
          <button onClick={() => processVoiceCommand('What is the call status')} className="text-left hover:text-gold">
            • "What is the call status?"
          </button>
          <button onClick={() => processVoiceCommand('Revenue report')} className="text-left hover:text-gold">
            • "Revenue report"
          </button>
          <button onClick={() => processVoiceCommand('ROI update')} className="text-left hover:text-gold">
            • "ROI update"
          </button>
          <button onClick={() => processVoiceCommand('Instagram analytics')} className="text-left hover:text-gold">
            • "Instagram analytics"
          </button>
          <button onClick={() => processVoiceCommand('Hermes status')} className="text-left hover:text-gold">
            • "Hermes status"
          </button>
        </div>
      </div>
    </div>
  );
}
