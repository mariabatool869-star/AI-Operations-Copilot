import { useEffect, useRef } from "react";
import Message from "./Message.jsx";

export default function MessageList({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  return (
    <div className="message-list" role="log" aria-live="polite">
      {messages.length === 0 && !loading && (
        <div className="empty-state">
          <p className="empty-title">Industrial asset monitoring</p>
          <p className="empty-subtitle">
            Ask about pumps, compressors, and tanks — sensors, failure risk, and
            maintenance history.
          </p>
          <p className="empty-hint">Known assets: P-104 · C-7 · P-22 · T-12</p>
        </div>
      )}

      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}

      {loading && (
        <div className="message-row message-row-copilot">
          <div className="message-bubble bubble-copilot typing-bubble">
            <div className="thinking">
              <span className="spinner" aria-hidden="true" />
              <span>Thinking</span>
              <span className="typing-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
