import { useCallback, useEffect, useRef, useState } from "react";
import Header from "./components/Header.jsx";
import MessageList from "./components/MessageList.jsx";
import ExampleChips from "./components/ExampleChips.jsx";
import InputArea from "./components/InputArea.jsx";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8002").replace(
  /\/$/,
  ""
);
const STORAGE_KEY = "ai-ops-copilot-messages";

function loadMessages() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export default function App() {
  const [messages, setMessages] = useState(loadMessages);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);
  const [mode, setMode] = useState("");
  const [lastQuestion, setLastQuestion] = useState(null);
  const inputRef = useRef(null);

  // Persist chat for the browser session
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {
      /* ignore quota errors */
    }
  }, [messages]);

  // Auto-focus input
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Poll health for Live badge
  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error("unhealthy");
        const data = await res.json();
        if (!cancelled) {
          setConnected(true);
          setMode(data.mode || "");
        }
      } catch {
        if (!cancelled) {
          setConnected(false);
          setMode("");
        }
      }
    }

    checkHealth();
    const id = setInterval(checkHealth, 15000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const ask = useCallback(async (question) => {
    const q = question.trim();
    if (!q || loading) return;

    setError(null);
    setLastQuestion(q);
    setDraft("");
    setLoading(true);

    const userMsg = {
      id: uid(),
      role: "user",
      content: q,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      let payload = null;
      try {
        payload = await res.json();
      } catch {
        payload = null;
      }

      if (!res.ok) {
        const detail =
          (payload && (payload.detail || payload.message)) ||
          `Request failed (${res.status})`;
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      }

      const answer = payload?.answer;
      if (!answer) throw new Error("Empty response from API.");

      setMessages((prev) => [
        ...prev,
        {
          id: uid(),
          role: "copilot",
          content: answer,
          timestamp: Date.now(),
        },
      ]);
      setConnected(true);
    } catch (err) {
      setError(err?.message || "Something went wrong. Check that the API is running.");
    } finally {
      setLoading(false);
      // Refocus after response for continuous Q&A
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [loading]);

  function handleSubmit() {
    ask(draft);
  }

  function handleRetry() {
    if (lastQuestion) ask(lastQuestion);
  }

  function handleClearDraft() {
    setDraft("");
  }

  return (
    <div className="app-shell">
      <div className="app-bg" aria-hidden="true" />
      <Header connected={connected} mode={mode} />

      <main className="app-main">
        <MessageList messages={messages} loading={loading} />

        {error && (
          <div className="error-banner" role="alert">
            <div className="error-text">
              <strong>Could not get a response.</strong>
              <span>{error}</span>
            </div>
            <button type="button" className="retry-btn" onClick={handleRetry} disabled={loading}>
              Retry
            </button>
          </div>
        )}

        <ExampleChips onSelect={ask} disabled={loading} />
        <InputArea
          ref={inputRef}
          value={draft}
          onChange={setDraft}
          onSubmit={handleSubmit}
          onClear={handleClearDraft}
          disabled={loading}
        />
        <p className="footer-note">
          Assistive only — confirm maintenance decisions with a qualified engineer.
        </p>
      </main>
    </div>
  );
}
