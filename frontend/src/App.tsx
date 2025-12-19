import { useMemo, useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getToken, getUser, logout } from "./lib/auth";
import { parseSseStream } from "./lib/sse";
import "./App.css";

type ChatMsg = { role: "user" | "assistant"; content: string };

export default function Chat() {
  const navigate = useNavigate();
  const apiBase = useMemo(
    () => import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
    []
  );
  const user = getUser();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Verify authentication on mount
  useEffect(() => {
    const token = getToken();
    if (!token) {
      logout();
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      role: "assistant",
      content:
        "Hi! Ask about a medication (ingredients, label instructions), stock availability, or prescription requirements.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolStatus, setToolStatus] = useState<string | null>(null);
  const [localeHint, setLocaleHint] = useState<"en" | "he">(
    (user?.preferred_language as "en" | "he") || "en"
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || isStreaming) return;

    setToolStatus(null);
    setIsStreaming(true);
    setInput("");

    const nextMessages: ChatMsg[] = [...messages, { role: "user", content: text }];
    // Add a streaming assistant message placeholder.
    setMessages([...nextMessages, { role: "assistant", content: "" }]);

    const token = getToken();
    if (!token) {
      navigate("/", { replace: true });
      return;
    }

    const res = await fetch(`${apiBase}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        messages: nextMessages,
        localeHint: localeHint,
      }),
    });

    if (!res.ok || !res.body) {
      setIsStreaming(false);
      setToolStatus(null);
      if (res.status === 401) {
        // Token expired or invalid
        logout();
        navigate("/", { replace: true });
        return;
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${res.status} ${res.statusText}` },
      ]);
      return;
    }

    try {
      for await (const evt of parseSseStream(res.body)) {
        if (evt.event === "delta" && evt.data?.text) {
          const deltaText = String(evt.data.text);
          setMessages((prev) => {
            const copy = [...prev];
            const idx = copy.length - 1;
            if (copy[idx]?.role !== "assistant") return prev;
            copy[idx] = { ...copy[idx], content: copy[idx].content + deltaText };
            return copy;
          });
        }

        if (evt.event === "tool_status" && evt.data?.tool) {
          const status = evt.data?.status === "running" ? "Running" : "Done";
          setToolStatus(`${status}: ${evt.data.tool}`);
        }

        if (evt.event === "error" && evt.data?.message) {
          setToolStatus(null);
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: `Error: ${evt.data.message}` },
          ]);
        }

        if (evt.event === "done") break;
      }
    } finally {
      setIsStreaming(false);
      setToolStatus(null);
    }
  }

  function reset() {
    if (isStreaming) return;
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! Ask about a medication (ingredients, label instructions), stock availability, or prescription requirements.",
      },
    ]);
    setToolStatus(null);
    setInput("");
  }

  return (
    <div className="page">
      <header className="topbar">
        <div className="title">Rotem&apos;s Pharmacy Agent</div>
        <div className="controls">
          {user && <span className="user-info">{user.full_name}</span>}
          <select
            value={localeHint}
            onChange={(e) => setLocaleHint(e.target.value as "en" | "he")}
            disabled={isStreaming}
            aria-label="Language"
          >
            <option value="en">English</option>
            <option value="he">עברית</option>
          </select>
          <button onClick={reset} disabled={isStreaming}>
            Reset
          </button>
          <button
            onClick={() => {
              logout();
              navigate("/", { replace: true });
            }}
            disabled={isStreaming}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="chat">
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="bubble">{m.content}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="status">
          {isStreaming ? "Thinking…" : "Ready"}
          {toolStatus ? ` • ${toolStatus}` : ""}
        </div>

        <div className="composer">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message…"
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
            disabled={isStreaming}
          />
          <button onClick={send} disabled={isStreaming || !input.trim()}>
            Send
          </button>
        </div>
      </main>
    </div>
  );
}


