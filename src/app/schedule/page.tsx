"use client";

import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import type { ScheduledMessage, Sponsor } from "@/lib/types";

export default function SchedulePage() {
  const [pending, setPending]   = useState<ScheduledMessage[]>([]);
  const [history, setHistory]   = useState<ScheduledMessage[]>([]);
  const [sponsors, setSponsors] = useState<Sponsor[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [sending, setSending]   = useState(false);
  const [loading, setLoading]   = useState(true);

  // Form state
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
  const blank = { recipient: "", channel: "Email", message: "", send_date: tomorrow.toISOString().split("T")[0], send_time: "09:00" };
  const [form, setForm] = useState(blank);
  const setF = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const load = useCallback(async () => {
    const [pRes, hRes, spRes] = await Promise.all([
      fetch("/api/scheduled-messages?status=pending").then((r) => r.json()),
      fetch("/api/scheduled-messages").then((r) => r.json()),
      fetch("/api/sponsors").then((r) => r.json()),
    ]);
    if (pRes.success) setPending(pRes.data);
    if (hRes.success) setHistory(hRes.data.filter((m: ScheduledMessage) => m.status !== "pending"));
    if (spRes.success) { setSponsors(spRes.data); if (spRes.data[0]) setForm((f) => ({ ...f, recipient: spRes.data[0].name })); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const schedule = async () => {
    const sendTime = new Date(`${form.send_date}T${form.send_time}`).toISOString();
    const res = await fetch("/api/scheduled-messages", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipient: form.recipient, channel: form.channel, message: form.message, send_time: sendTime }),
    }).then((r) => r.json());
    if (res.success) { toast.success("✅ Scheduled!"); setShowForm(false); setForm(blank); load(); }
    else toast.error(res.error ?? "Failed");
  };

  const sendNow = async (msg: ScheduledMessage) => {
    setSending(true);
    // Update status triggers worker
    const res = await fetch(`/api/scheduled-messages/${msg.id}`, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "pending" }),
    }).then((r) => r.json());

    // Actually send it via worker
    const workerRes = await fetch("/api/worker", { method: "POST" }).then((r) => r.json());
    setSending(false);
    if (workerRes.success) { toast.success("Sent!"); load(); }
    else toast.error("Send failed");
    void res;
  };

  const cancel = async (id: number) => {
    const res = await fetch(`/api/scheduled-messages/${id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) { toast.success("Cancelled"); load(); }
    else toast.error(res.error ?? "Failed");
  };

  const runDue = async () => {
    setSending(true);
    const res = await fetch("/api/worker", { method: "POST" }).then((r) => r.json());
    setSending(false);
    if (res.success) {
      const { processed } = res.data;
      toast.success(`✅ Processed ${processed} message(s)`);
      load();
    } else toast.error(res.error ?? "Failed");
  };

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Scheduled <span className="accent">Messages</span></div>
          <div className="page-subtitle">Queue and automate sponsor communications</div>
        </div>
        <div style={{ display: "flex", gap: "0.75rem", paddingTop: "0.5rem" }}>
          <button className="btn btn-secondary" onClick={runDue} disabled={sending}>
            {sending ? <span className="spinner" /> : "📤"} Send All Due Now
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>➕ New Scheduled Message</button>
        </div>
      </div>

      {/* Schedule form */}
      {showForm && (
        <div className="hope-card fade-in">
          <div className="section-subheader" style={{ marginTop: 0 }}>New Scheduled Message</div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Recipient</label>
              <select className="form-select" value={form.recipient} onChange={(e) => setF("recipient", e.target.value)}>
                {sponsors.map((s) => <option key={s.id} value={s.name}>{s.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Channel</label>
              <select className="form-select" value={form.channel} onChange={(e) => setF("channel", e.target.value)}>
                <option value="Email">📧 Email</option>
                <option value="WhatsApp">💬 WhatsApp</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Send Date</label>
              <input className="form-input" type="date" value={form.send_date} onChange={(e) => setF("send_date", e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Send Time</label>
              <input className="form-input" type="time" value={form.send_time} onChange={(e) => setF("send_time", e.target.value)} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Message</label>
            <textarea className="form-textarea" rows={4} value={form.message} onChange={(e) => setF("message", e.target.value)} />
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button className="btn btn-primary" onClick={schedule} disabled={!form.recipient || !form.message.trim()}>Schedule</button>
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <hr />

      {/* Pending messages */}
      <div className="section-subheader">⏳ Pending ({pending.length})</div>
      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem" }}><span className="spinner" /> Loading…</div>
      ) : pending.length > 0 ? (
        <div className="hope-card">
          {pending.map((msg) => (
            <div className="activity-row" key={msg.id}>
              <div className="activity-left" style={{ flex: 1 }}>
                <div className="activity-avatar">{msg.recipient?.charAt(0).toUpperCase() ?? "?"}</div>
                <div style={{ flex: 1 }}>
                  <div className="activity-name">{msg.recipient}</div>
                  <div className="activity-excerpt">{msg.message?.slice(0, 70)}{(msg.message?.length ?? 0) > 70 ? "…" : ""}</div>
                  <div className="activity-meta">📅 {new Date(msg.send_time).toLocaleString()}</div>
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexShrink: 0 }}>
                <span className={`badge ${msg.channel === "Email" ? "badge-purple" : "badge-warning"}`}>{msg.channel}</span>
                <button className="btn btn-primary btn-sm" onClick={() => sendNow(msg)} disabled={sending}>Send Now</button>
                <button className="btn btn-danger btn-sm" onClick={() => cancel(msg.id)}>Cancel</button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-desc">No pending scheduled messages.</div>
        </div>
      )}

      {/* History */}
      <div style={{ marginTop: "1rem" }}>
        <button className="btn btn-secondary btn-sm" onClick={() => setShowHistory(!showHistory)}>
          {showHistory ? "▲" : "▼"} History ({history.length})
        </button>
        {showHistory && history.length > 0 && (
          <div className="hope-card fade-in" style={{ marginTop: "0.75rem", overflowX: "auto" }}>
            <table className="hope-table">
              <thead>
                <tr><th>Recipient</th><th>Channel</th><th>Message</th><th>Send Time</th><th>Status</th></tr>
              </thead>
              <tbody>
                {history.map((m) => (
                  <tr key={m.id}>
                    <td>{m.recipient}</td>
                    <td>{m.channel}</td>
                    <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{m.message}</td>
                    <td style={{ fontSize: "0.82rem" }}>{new Date(m.send_time).toLocaleString()}</td>
                    <td>
                      <span className={`badge ${m.status === "sent" ? "badge-success" : m.status === "cancelled" ? "badge-danger" : "badge-warning"}`}>
                        {m.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
