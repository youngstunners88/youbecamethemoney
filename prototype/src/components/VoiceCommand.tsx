import { useState, useRef } from 'react';
import { mockHermesAPI } from '../api/mockHermes';

interface CommandHistory {
  command: string;
  response: string;
  timestamp: string;
}

export default function VoiceCommand() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [history, setHistory] = useState<CommandHistory[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleVoiceToggle = () => {
    if (!isListening) {
      setIsListening(true);
      // Simulate voice recognition for prototype
      setTimeout(() => {
        setTranscript('Show me high urgency leads from this week');
        setIsListening(false);
      }, 2000);
    } else {
      setIsListening(false);
    }
  };

  const sendCommand = async () => {
    if (!transcript.trim()) return;
    
    setIsProcessing(true);
    
    try {
      const result = await mockHermesAPI.sendVoiceCommand(transcript);
      
      setHistory(prev => [{
        command: transcript,
        response: result.response,
        timestamp: result.timestamp
      }, ...prev].slice(0, 10));
      
      setTranscript('');
    } catch (error) {
      console.error('Command failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const quickCommands = [
    'Show urgent leads',
    'What\'s my pipeline value?',
    'Recent consultations',
    'Leads from WhatsApp today'
  ];

  return (
    <div className="bg-navy-800 rounded-xl border border-gold/20 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-serif font-bold text-gold">Voice Command</h2>
          <p className="text-gray-400 text-sm">Talk to Hermes agent</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isListening ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></span>
          <span className="text-xs text-gray-400">{isListening ? 'Listening...' : 'Ready'}</span>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <button
          onClick={handleVoiceToggle}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
            isListening 
              ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
              : 'bg-gold hover:bg-gold-light'
          }`}
        >
          <svg className="w-8 h-8 text-navy-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>

        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder={isListening ? 'Listening...' : 'Say something or type a command...'}
            className="w-full h-16 bg-navy-900 border border-gold/20 rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none focus:border-gold resize-none"
          />
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs text-gray-500">Try: "Show urgent leads" or "Pipeline value"</span>
            <button
              onClick={sendCommand}
              disabled={!transcript.trim() || isProcessing}
              className="px-4 py-2 bg-gold text-navy-900 font-semibold rounded-lg hover:bg-gold-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {history.map((item, index) => (
              <div key={index} className="border-l-2 border-gold pl-3">
                <p className="text-gray-400 text-xs mb-1">
                  {new Date(item.timestamp).toLocaleTimeString()}
                </p>
                <p className="text-white text-sm font-medium">"{item.command}"</p>
                <p className="text-gold text-sm mt-1">{item.response}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
