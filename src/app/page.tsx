"use client";

import { useEffect, useState } from "react";
import type { DashboardStats } from "@/lib/types";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

function StatCard({ icon, value, label }: { icon: string; value: number; label: string }) {
  return (
    <div className="stat-card fade-in">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function getBadgeCls(status: string) {
  const s = status.toLowerCase();
  if (s === "sent") return "badge-success";
  if (s === "pending") return "badge-warning";
  if (s === "failed") return "badge-danger";
  return "badge-purple";
}

function getChannelBadgeCls(channel: string) {
  return channel.toLowerCase().includes("email") ? "badge-purple" : "badge-warning";
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    fetch("/api/dashboard")
      .then((r) => r.json())
      .then((d) => { if (d.success) setStats(d.data); })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 30_000); // auto-refresh every 30 s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fade-in">
      {/* Header */}
      <div style={{ marginBottom: "1.75rem" }}>
        <div className="page-title">
          Welcome to <span className="accent">HOPe</span>
        </div>
        <div className="page-subtitle">
          Your sponsor relationship &amp; student support dashboard
        </div>
      </div>

      {loading && !stats ? (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: "#64748B" }}>
          <span className="spinner" /> Loading…
        </div>
      ) : stats ? (
        <>
          {/* Stats row */}
          <div className="stat-grid">
            <StatCard icon="👥" value={stats.totalSponsors}    label="Total Sponsors" />
            <StatCard icon="🎓" value={stats.totalStudents}    label="Students Supported" />
            <StatCard icon="💬" value={stats.totalMessages}    label="Messages Sent" />
            <StatCard icon="⏳" value={stats.pendingScheduled} label="Pending Action" />
          </div>

          {/* Chart */}
          {stats.messagesByDay.length > 0 && (
            <div className="chart-container fade-in" style={{ marginBottom: "2rem" }}>
              <div className="section-subheader" style={{ marginTop: 0, marginBottom: "1rem" }}>
                📈 Message Activity (last 30 days)
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={stats.messagesByDay} margin={{ top: 5, right: 10, left: -30, bottom: 0 }}>
                  <defs>
                    <linearGradient id="msgGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#7C3AED" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}    />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.1)" />
                  <XAxis dataKey="date" tick={{ fill: "#64748B", fontSize: 11 }} tickLine={false} />
                  <YAxis tick={{ fill: "#64748B", fontSize: 11 }} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ background: "#1E1B4B", border: "1px solid rgba(139,92,246,0.35)", borderRadius: "8px", color: "#F1F5F9", fontSize: "0.85rem" }}
                    cursor={{ stroke: "rgba(139,92,246,0.3)" }}
                  />
                  <Area type="monotone" dataKey="count" stroke="#7C3AED" strokeWidth={2} fill="url(#msgGrad)" name="Messages" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Recent activity */}
          <div className="section-subheader">Recent Activity</div>
          {stats.recentMessages.length > 0 ? (
            <div className="hope-card">
              {stats.recentMessages.map((msg) => {
                const avatar = msg.recipient?.trim()?.charAt(0)?.toUpperCase() ?? "?";
                const excerpt = msg.message?.length > 90
                  ? msg.message.slice(0, 90) + "…"
                  : (msg.message ?? "");
                return (
                  <div className="activity-row" key={msg.id}>
                    <div className="activity-left">
                      <div className="activity-avatar">{avatar}</div>
                      <div>
                        <div className="activity-name">{msg.recipient || "—"}</div>
                        <div className="activity-excerpt">{excerpt}</div>
                        <div className="activity-meta">{msg.date}</div>
                      </div>
                    </div>
                    <div className="activity-badges">
                      <span className={`badge ${getChannelBadgeCls(msg.channel ?? "")}`}>
                        {msg.channel}
                      </span>
                      <span className={`badge ${getBadgeCls(msg.status ?? "")}`}>
                        {msg.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="hope-card empty-state">
              <div className="empty-icon">📭</div>
              <div className="empty-title">No recent activity yet</div>
              <div className="empty-desc">Start by adding a sponsor!</div>
            </div>
          )}
        </>
      ) : (
        <div className="alert alert-error">Failed to load dashboard data.</div>
      )}
    </div>
  );
}
