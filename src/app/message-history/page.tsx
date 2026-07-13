"use client";

import { useEffect, useState } from "react";
import type { MessageRecord } from "@/lib/types";

function getBadgeCls(status: string) {
  const s = status?.toLowerCase() ?? "";
  if (s === "sent") return "badge-success";
  if (s === "failed") return "badge-danger";
  return "badge-warning";
}

function getChannelCls(channel: string) {
  return (channel ?? "").toLowerCase().includes("email") ? "badge-purple" : "badge-warning";
}

export default function MessageHistoryPage() {
  const [messages, setMessages] = useState<MessageRecord[]>([]);
  const [search, setSearch]     = useState("");
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    fetch("/api/messages").then((r) => r.json()).then((d) => {
      if (d.success) setMessages(d.data);
      setLoading(false);
    });
  }, []);

  const filtered = messages.filter((m) =>
    !search ||
    [m.recipient, m.channel, m.message, m.status, m.date].some((v) =>
      (v ?? "").toLowerCase().includes(search.toLowerCase())
    )
  );

  const exportCSV = () => {
    const header = ["ID", "Date", "Recipient", "Channel", "Direction", "Message", "Status"];
    const rows = filtered.map((m) => [m.id, m.date, m.recipient, m.channel, m.direction, m.message, m.status].map(String));
    const csv = [header, ...rows].map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "message-history.csv"; a.click();
  };

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Message <span className="accent">History</span></div>
          <div className="page-subtitle">Full log of all messages sent through HOPe</div>
        </div>
        <div style={{ paddingTop: "0.5rem" }}>
          <button className="btn btn-secondary btn-sm" onClick={exportCSV}>⬇ Export CSV</button>
        </div>
      </div>

      <div className="search-bar">
        <span className="search-icon">🔍</span>
        <input className="form-input" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search messages…" />
      </div>

      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span className="spinner" /> Loading…
        </div>
      ) : filtered.length > 0 ? (
        <div className="hope-card" style={{ overflowX: "auto" }}>
          <table className="hope-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Recipient</th>
                <th>Channel</th>
                <th>Direction</th>
                <th>Message</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((m) => (
                <tr key={m.id}>
                  <td style={{ fontSize: "0.82rem", whiteSpace: "nowrap" }}>{m.date}</td>
                  <td style={{ fontWeight: 600, color: "#E2E8F0" }}>{m.recipient}</td>
                  <td><span className={`badge ${getChannelCls(m.channel)}`}>{m.channel}</span></td>
                  <td><span className="badge badge-purple">{m.direction}</span></td>
                  <td style={{ maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={m.message}>{m.message}</td>
                  <td><span className={`badge ${getBadgeCls(m.status)}`}>{m.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ fontSize: "0.78rem", color: "#64748B", marginTop: "0.75rem" }}>
            {filtered.length} message{filtered.length !== 1 ? "s" : ""} {search ? `matching "${search}"` : "total"}
          </div>
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">📜</div>
          <div className="empty-title">{search ? "No messages match" : "No messages logged yet"}</div>
          <div className="empty-desc">{search ? "Try a different search term" : "Send a message to see it here."}</div>
        </div>
      )}
    </div>
  );
}
