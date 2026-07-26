import { useState } from "react";
import Markdown from "./Markdown.jsx";

export default function Message({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";
  const timeLabel = formatTime(message.timestamp);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard may be blocked */
    }
  }

  return (
    <div className={`message-row ${isUser ? "message-row-user" : "message-row-copilot"}`}>
      <div className={`message-bubble ${isUser ? "bubble-user" : "bubble-copilot"}`}>
        {!isUser && (
          <div className="message-meta">
            <span className="message-sender">Copilot</span>
            {timeLabel && <span className="message-time">{timeLabel}</span>}
            <button
              type="button"
              className="copy-btn"
              onClick={handleCopy}
              aria-label="Copy response"
              title="Copy"
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        )}
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : (
          <Markdown content={message.content} />
        )}
        {isUser && timeLabel && (
          <span className="message-time message-time-user">{timeLabel}</span>
        )}
      </div>
    </div>
  );
}

function formatTime(ts) {
  if (!ts) return "";
  try {
    return new Date(ts).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}
