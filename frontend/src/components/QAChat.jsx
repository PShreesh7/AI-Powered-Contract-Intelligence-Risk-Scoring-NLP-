import { useState, useRef, useEffect } from 'react';
import { askContractQuestion } from '../api/client.js';

const SUGGESTED_QUESTIONS = [
  'What are the termination conditions?',
  'Are there any auto-renewal clauses?',
  'What is the liability cap?',
  'Who controls the dispute resolution venue?',
];

export default function QAChat({ clauseTexts }) {
  const [messages, setMessages]     = useState([]);
  const [inputText, setInputText]   = useState('');
  const [isTyping, setIsTyping]     = useState(false);
  const messagesEndRef              = useRef(null);
  const textareaRef                 = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  async function sendMessage(question) {
    const q = (question ?? inputText).trim();
    if (!q) return;

    setInputText('');
    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setIsTyping(true);

    try {
      const answer = await askContractQuestion(clauseTexts, q);
      setMessages(prev => [...prev, { role: 'ai', text: answer }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'ai',
        text: `⚠️ Could not get an answer: ${err.message}. Make sure the backend is running.`,
        isError: true,
      }]);
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

  function autoResize(e) {
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
    setInputText(ta.value);
  }

  return (
    <div className="qa-panel">
      {/* Messages area */}
      <div className="qa-messages" role="log" aria-live="polite" aria-label="Contract Q&A conversation">
        {messages.length === 0 && (
          <div className="qa-welcome">
            <div className="qa-welcome-icon">🤖</div>
            <div className="qa-welcome-title">Ask anything about this contract</div>
            <p className="qa-welcome-sub">
              Our AI (powered by Gemini) will analyze the contract clauses and answer your question in plain language.
            </p>
            <div className="qa-suggestions" role="list">
              {SUGGESTED_QUESTIONS.map(q => (
                <button
                  key={q}
                  className="qa-suggest-btn"
                  onClick={() => sendMessage(q)}
                  role="listitem"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="msg-avatar" aria-hidden="true">
              {msg.role === 'user' ? '👤' : '⚖️'}
            </div>
            <div className={`msg-bubble ${msg.isError ? 'error' : ''}`} role="article">
              {msg.text}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="message ai">
            <div className="msg-avatar" aria-hidden="true">⚖️</div>
            <div className="msg-bubble" aria-label="AI is typing">
              <div className="msg-typing">
                <div className="msg-dot" />
                <div className="msg-dot" />
                <div className="msg-dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="qa-input-area">
        <textarea
          id="qa-input"
          ref={textareaRef}
          className="qa-textarea"
          value={inputText}
          onChange={autoResize}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about this contract…"
          rows={1}
          aria-label="Question input"
          disabled={isTyping}
        />
        <button
          id="qa-send-btn"
          className="qa-send-btn"
          onClick={() => sendMessage()}
          disabled={isTyping || !inputText.trim()}
          aria-label="Send question"
        >
          {isTyping ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
}
