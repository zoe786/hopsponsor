"use client";

import { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import type { ChatMessage, StyleEntry } from "@/lib/types";

type Tab = "draft" | "chat";

export default function AIPage() {
  const [tab, setTab] = useState<Tab>("draft");
  const [styles, setStyles] = useState<StyleEntry[]>([]);

  useEffect(() => {
    fetch("/api/styles").then((r) => r.json()).then((d) => { if (d.success) setStyles(d.data); });
  }, []);

  const styleExamples = styles.map((s) => s.message).join("\n---\n");

  return (
    <div className="fade-in">
      <div className="page-title">AI <span className="accent">Intelligence</span></div>
      <div className="page-subtitle">Generate sponsor messages and get AI-powered assistance</div>

      <div className="tabs">
        <button className={`tab-btn ${tab === "draft" ? "active" : ""}`} onClick={() => setTab("draft")}>
          ✍️  Draft Message
        </button>
        <button className={`tab-btn ${tab === "chat" ? "active" : ""}`} onClick={() => setTab("chat")}>
          💬  Chat Assistant
        </button>
      </div>

      {tab === "draft" ? (
        <DraftTab styleExamples={styleExamples} styles={styles} />
      ) : (
        <ChatTab styleExamples={styleExamples} />
      )}
    </div>
  );
}

function DraftTab({ styleExamples, styles }: { styleExamples: string; styles: StyleEntry[] }) {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [draft, setDraft] = useState("");
  const [generating, setGenerating] = useState(false);

  const generate = async () => {
    if (!prompt.trim()) { toast.error("Enter a prompt first"); return; }
    setGenerating(true);
    const fd = new FormData();
    fd.append("prompt", prompt);
    fd.append("style_examples", styleExamples);
    if (image) fd.append("image", image);

    const res = await fetch("/api/ai/generate", { method: "POST", body: fd }).then((r) => r.json());
    setGenerating(false);
    if (res.success) { setDraft(res.data.draft); toast.success("Draft ready!"); }
    else toast.error(res.error ?? "Generation failed");
  };

  const copyDraft = () => {
    navigator.clipboard.writeText(draft).then(() => toast.success("Copied to clipboard!"));
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "5fr 4fr", gap: "1.5rem", alignItems: "start" }}>
      {/* Left: prompt */}
      <div>
        <div className="section-subheader" style={{ marginTop: 0 }}>Message Prompt</div>
        <div className="form-group">
          <textarea
            className="form-textarea"
            rows={6}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Write a warm update for our sponsor thanking them for their contribution this month…"
          />
        </div>
        <div className="form-group">
          <label className="form-label">Attach image (optional)</label>
          <label className="file-upload-area" style={{ display: "block", cursor: "pointer", padding: "1rem" }}>
            <input type="file" accept="image/*" style={{ display: "none" }} onChange={(e) => setImage(e.target.files?.[0] ?? null)} />
            {image ? (
              <span style={{ color: "#C4B5FD" }}>📷 {image.name}</span>
            ) : (
              <span style={{ color: "#64748B", fontSize: "0.875rem" }}>Click to attach an image</span>
            )}
          </label>
        </div>

        {/* Style reference chips */}
        {styles.length > 0 && (
          <>
            <div className="section-subheader">Reference Styles</div>
            {styles.slice(0, 5).map((s) => (
              <div key={s.id} style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(139,92,246,0.2)", borderRadius: "10px", padding: "0.65rem 0.75rem", marginBottom: "0.5rem" }}>
                <div style={{ color: "#DDD6FE", fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.25rem" }}>
                  {s.golden_example ? "⭐ " : ""}{s.category}
                </div>
                <div style={{ color: "#94A3B8", fontSize: "0.8rem", lineHeight: 1.4 }}>
                  {s.message.slice(0, 90)}{s.message.length > 90 ? "…" : ""}
                </div>
              </div>
            ))}
          </>
        )}

        <button className="btn btn-primary btn-full" onClick={generate} disabled={generating}>
          {generating ? <><span className="spinner" /> Generating…</> : "✨ Generate Draft"}
        </button>
      </div>

      {/* Right: output */}
      <div>
        <div className="section-subheader" style={{ marginTop: 0 }}>Generated Output</div>
        {draft ? (
          <div className="hope-card fade-in">
            <div style={{ color: "#E2E8F0", lineHeight: 1.7, whiteSpace: "pre-wrap", fontSize: "0.9rem" }}>
              {draft}
            </div>
            <button className="btn btn-secondary btn-full" style={{ marginTop: "1rem" }} onClick={copyDraft}>
              📋 Copy to Clipboard
            </button>
          </div>
        ) : (
          <div className="hope-card" style={{ textAlign: "center", padding: "3rem 1rem", minHeight: "200px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>✨</div>
            <div style={{ color: "#64748B", fontSize: "0.875rem" }}>Your generated draft will appear here</div>
          </div>
        )}
      </div>
    </div>
  );
}

function ChatTab({ styleExamples }: { styleExamples: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setSending(true);

    const res = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: [...messages, userMsg], style_examples: styleExamples }),
    }).then((r) => r.json());

    setSending(false);
    if (res.success) {
      setMessages((m) => [...m, { role: "assistant", content: res.data.response }]);
    } else {
      toast.error(res.error ?? "Chat error");
    }
  };

  return (
    <div>
      {/* Chat history */}
      <div className="chat-container" style={{ minHeight: 200, maxHeight: 500, overflowY: "auto", marginBottom: "1rem" }}>
        {messages.length === 0 ? (
          <div className="hope-card" style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{ fontSize: "1.8rem", marginBottom: "0.5rem" }}>🤖</div>
            <div style={{ color: "#94A3B8", fontSize: "0.875rem" }}>
              Ask me anything about your sponsors, students, or request a message draft.
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div className={`chat-msg fade-in`} key={i}>
              <div className={`chat-avatar ${msg.role}`}>{msg.role === "user" ? "U" : "AI"}</div>
              <div className={`chat-bubble ${msg.role}`}>{msg.content}</div>
            </div>
          ))
        )}
        {sending && (
          <div className="chat-msg fade-in">
            <div className="chat-avatar ai">AI</div>
            <div className="chat-bubble" style={{ color: "#64748B" }}>
              <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="chat-input-row">
        <input
          className="form-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
          placeholder="Ask me anything about sponsors, students, or messaging…"
          disabled={sending}
        />
        <button className="btn btn-primary" onClick={send} disabled={sending || !input.trim()}>Send</button>
        <button className="btn btn-secondary" onClick={() => setMessages([])}>Clear</button>
      </div>
    </div>
  );
}
