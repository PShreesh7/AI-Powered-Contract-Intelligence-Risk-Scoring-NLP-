import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import { askContractQuestion } from '../api/client.js';
import Card3D from './Card3D.jsx';

const SUGGESTED_QUESTIONS = [
  'What are the termination conditions & notice periods?',
  'Is liability capped or is there uncapped indemnification?',
  'Are there automatic renewals or non-compete clauses?',
  'Which state or country laws govern this contract?',
];

export default function QAChat({ clauseTexts = [] }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  async function sendMessage(question) {
    const q = (question ?? inputText).trim();
    if (!q) return;

    setInputText('');
    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    setIsTyping(true);

    try {
      const answer = await askContractQuestion(clauseTexts, q);
      setMessages((prev) => [...prev, { role: 'ai', text: answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: err.message || 'Unable to reach the Gemini Q&A model. Please check GOOGLE_API_KEY.',
          isError: true,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="qa-panel-3d">
      {/* Messages area */}
      <div className="qa-chat-scroll" role="log" aria-live="polite">
        {messages.length === 0 && (
          <div className="qa-empty-hero">
            <div className="qa-hero-orb">
              <Sparkles size={28} className="text-accent" />
            </div>
            <h3 className="qa-hero-title">Grounded Contract Intelligence Chat</h3>
            <p className="qa-hero-desc">
              Ask specific legal questions in plain English. Powered by Google Gemini, answers are
              strictly derived and cited from your ingested contract provisions.
            </p>

            <div className="qa-suggestions-grid">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="qa-prompt-chip"
                  onClick={() => sendMessage(q)}
                >
                  <Sparkles size={13} className="text-accent" />
                  <span>{q}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble-row ${msg.role === 'user' ? 'is-user' : 'is-ai'}`}>
            <div className="chat-avatar">
              {msg.role === 'user' ? (
                <User size={15} />
              ) : (
                <Bot size={15} className="text-accent" />
              )}
            </div>
            <div className={`chat-message-bubble ${msg.isError ? 'is-error' : ''}`}>
              {msg.isError && <AlertCircle size={15} className="error-icon" />}
              <p className="bubble-text">{msg.text}</p>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="chat-bubble-row is-ai">
            <div className="chat-avatar">
              <Bot size={15} className="text-accent" />
            </div>
            <div className="chat-message-bubble is-typing">
              <div className="typing-pulse">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
              <span className="typing-label">Analyzing clauses with Gemini…</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input box */}
      <div className="qa-input-tray">
        <div className="qa-input-card">
          <textarea
            rows={1}
            placeholder="Ask a question about termination, liability, payment, or parties…"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            type="button"
            className="qa-send-btn"
            disabled={!inputText.trim() || isTyping}
            onClick={() => sendMessage()}
            title="Send query"
          >
            {isTyping ? <Loader2 size={16} className="spin-icon" /> : <Send size={16} />}
          </button>
        </div>
        <div className="qa-input-footnote">
          Press Enter to send · Grounded in {clauseTexts.length} segmented contract clauses
        </div>
      </div>
    </div>
  );
}
