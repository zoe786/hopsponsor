"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import type { Sponsor } from "@/lib/types";

const TEMPLATES = [
  { label: "Thank You", text: "Dear {name},\n\nThank you so much for your generous sponsorship. Your support makes a real difference in the lives of the students you help.\n\nWarm regards,\nHOPe Team" },
  { label: "Monthly Update", text: "Dear {name},\n\nHere is your monthly update on the student(s) you sponsor. They are making wonderful progress and we are grateful for your continued support.\n\nKind regards,\nHOPe Team" },
  { label: "Event Invite", text: "Dear {name},\n\nWe would love to invite you to our upcoming event. It would mean so much to us and the students to have you there.\n\nPlease confirm your attendance at your earliest convenience.\n\nWarm regards,\nHOPe Team" },
];

export default function MessagesPage() {
  const [sponsors, setSponsors] = useState<Sponsor[]>([]);
  const [recipient, setRecipient] = useState("");
  const [channel, setChannel] = useState("Email");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetch("/api/sponsors").then((r) => r.json()).then((d) => {
      if (d.success) { setSponsors(d.data); if (d.data.length > 0) setRecipient(String(d.data[0].id)); }
    });
  }, []);

  const applyTemplate = (tpl: typeof TEMPLATES[0]) => {
    const sponsor = sponsors.find((s) => String(s.id) === recipient);
    const name = sponsor?.name ?? "Sponsor";
    setMessage(tpl.text.replace(/{name}/g, name));
    if (tpl.label !== "Monthly Update") setSubject(tpl.label);
  };

  const sendMessage = async () => {
    if (!recipient || !message.trim()) { toast.error("Select a recipient and enter a message"); return; }
    setSending(true);
    const res = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipient: Number(recipient), channel, subject, message }),
    }).then((r) => r.json());
    setSending(false);
    if (res.success) {
      toast.success(`✅ ${channel} sent!`);
      setMessage(""); setSubject("");
    } else {
      toast.error(res.error ?? "Failed to send");
    }
  };

  if (!sponsors.length) {
    return (
      <div className="fade-in">
        <div className="page-title">Compose <span className="accent">Message</span></div>
        <div className="hope-card" style={{ textAlign: "center", padding: "2.5rem" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>⚠️</div>
          <div style={{ color: "#FCD34D" }}>No sponsors found. Add sponsors first.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="page-title">Compose <span className="accent">Message</span></div>
      <div className="page-subtitle">Send emails or WhatsApp messages directly to sponsors</div>

      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: "1.5rem", alignItems: "start" }}>
        {/* Compose form */}
        <div className="hope-card">
          <div className="form-group">
            <label className="form-label">Recipient</label>
            <select className="form-select" value={recipient} onChange={(e) => setRecipient(e.target.value)}>
              {sponsors.map((s) => <option key={s.id} value={s.id}>{s.name}{s.company ? ` — ${s.company}` : ""}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Channel</label>
            <select className="form-select" value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="Email">📧 Email</option>
              <option value="WhatsApp">💬 WhatsApp</option>
            </select>
          </div>
          {channel === "Email" && (
            <div className="form-group">
              <label className="form-label">Subject</label>
              <input className="form-input" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Email subject…" />
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Message</label>
            <textarea className="form-textarea" rows={7} value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Type your message here…" />
          </div>
          <button className="btn btn-primary btn-full" onClick={sendMessage} disabled={sending}>
            {sending ? <span className="spinner" /> : "📤"} Send Message
          </button>

          {/* Selected sponsor info */}
          {recipient && (() => {
            const sp = sponsors.find((s) => String(s.id) === recipient);
            if (!sp) return null;
            return (
              <div style={{ marginTop: "1rem", padding: "0.75rem", background: "rgba(124,58,237,0.08)", borderRadius: "8px", border: "1px solid rgba(139,92,246,0.18)", fontSize: "0.82rem", color: "#94A3B8" }}>
                {channel === "Email" ? (
                  sp.email ? <>📧 {sp.email}</> : <span style={{ color: "#FCA5A5" }}>⚠️ No email on file</span>
                ) : (
                  sp.whatsapp ? <>💬 {sp.whatsapp}</> : <span style={{ color: "#FCA5A5" }}>⚠️ No WhatsApp on file</span>
                )}
              </div>
            );
          })()}
        </div>

        {/* Templates */}
        <div>
          <div className="section-subheader" style={{ marginTop: 0 }}>📋 Message Templates</div>
          {TEMPLATES.map((tpl) => (
            <div key={tpl.label} className="hope-card" style={{ cursor: "pointer", marginBottom: "0.75rem" }} onClick={() => applyTemplate(tpl)}>
              <div style={{ fontWeight: 600, color: "#C4B5FD", marginBottom: "0.35rem", fontSize: "0.85rem" }}>{tpl.label}</div>
              <div style={{ color: "#64748B", fontSize: "0.78rem", lineHeight: 1.4 }}>
                {tpl.text.slice(0, 80)}…
              </div>
            </div>
          ))}
          <div style={{ fontSize: "0.75rem", color: "#4B5563" }}>
            Click a template to apply it. <code>{"{name}"}</code> is replaced with the recipient&apos;s name.
          </div>
        </div>
      </div>
    </div>
  );
}
