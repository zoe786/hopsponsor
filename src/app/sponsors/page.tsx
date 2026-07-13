"use client";

import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import type { Sponsor } from "@/lib/types";

function SponsorForm({
  initial,
  onSave,
  onCancel,
  title,
}: {
  initial?: Partial<Sponsor>;
  onSave: (data: Partial<Sponsor>) => Promise<void>;
  onCancel: () => void;
  title: string;
}) {
  const [data, setData] = useState({
    name: initial?.name ?? "",
    company: initial?.company ?? "",
    whatsapp: initial?.whatsapp ?? "",
    email: initial?.email ?? "",
    notes: initial?.notes ?? "",
  });
  const [saving, setSaving] = useState(false);

  const set = (field: string, value: string) =>
    setData((d) => ({ ...d, [field]: value }));

  return (
    <div className="hope-card fade-in">
      <div className="section-subheader" style={{ marginTop: 0 }}>{title}</div>
      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Full Name *</label>
          <input className="form-input" value={data.name} onChange={(e) => set("name", e.target.value)} placeholder="e.g. Jane Doe" />
        </div>
        <div className="form-group">
          <label className="form-label">Company / Organisation</label>
          <input className="form-input" value={data.company} onChange={(e) => set("company", e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">WhatsApp Number</label>
          <input className="form-input" value={data.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} placeholder="+263..." />
        </div>
        <div className="form-group">
          <label className="form-label">Email Address</label>
          <input className="form-input" type="email" value={data.email} onChange={(e) => set("email", e.target.value)} />
        </div>
      </div>
      <div className="form-group">
        <label className="form-label">Notes</label>
        <textarea className="form-textarea" value={data.notes} onChange={(e) => set("notes", e.target.value)} rows={3} />
      </div>
      <div style={{ display: "flex", gap: "0.75rem" }}>
        <button
          className="btn btn-primary"
          disabled={saving || !data.name.trim()}
          onClick={async () => { setSaving(true); await onSave(data); setSaving(false); }}
        >
          {saving ? <span className="spinner" /> : null} Save
        </button>
        <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </div>
  );
}

export default function SponsorsPage() {
  const [sponsors, setSponsors] = useState<Sponsor[]>([]);
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [editing, setEditing] = useState<Sponsor | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    fetch("/api/sponsors").then((r) => r.json()).then((d) => {
      if (d.success) setSponsors(d.data);
    }).finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = sponsors.filter((s) =>
    !search || [s.name, s.company, s.email, s.whatsapp].some((v) =>
      (v ?? "").toLowerCase().includes(search.toLowerCase())
    )
  );

  const addSponsor = async (data: Partial<Sponsor>) => {
    const res = await fetch("/api/sponsors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
    if (res.success) { toast.success("Sponsor added!"); setShowAdd(false); load(); }
    else toast.error(res.error ?? "Failed");
  };

  const updateSponsor = async (data: Partial<Sponsor>) => {
    if (!editing) return;
    const res = await fetch(`/api/sponsors/${editing.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.json());
    if (res.success) { toast.success("Updated!"); setEditing(null); load(); }
    else toast.error(res.error ?? "Failed");
  };

  const deleteSponsor = async (sponsor: Sponsor) => {
    if (!confirm(`Delete sponsor "${sponsor.name}"? This cannot be undone.`)) return;
    const res = await fetch(`/api/sponsors/${sponsor.id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) { toast.success("Deleted"); load(); }
    else toast.error(res.error ?? "Failed");
  };

  // Export to CSV
  const exportCSV = () => {
    const header = ["ID", "Name", "Company", "WhatsApp", "Email", "Notes"];
    const rows = filtered.map((s) => [s.id, s.name, s.company, s.whatsapp, s.email, s.notes].map(String));
    const csv = [header, ...rows].map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "sponsors.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-header-row">
        <div>
          <div className="page-title">Sponsors</div>
          <div className="page-subtitle">Manage and track all your sponsor relationships</div>
        </div>
        <div style={{ display: "flex", gap: "0.75rem", paddingTop: "0.5rem" }}>
          <button className="btn btn-secondary btn-sm" onClick={exportCSV} title="Export to CSV">⬇ Export CSV</button>
          <button className="btn btn-primary" onClick={() => { setShowAdd(true); setEditing(null); }}>➕ Add Sponsor</button>
        </div>
      </div>

      {/* Search */}
      <div className="search-bar">
        <span className="search-icon">🔍</span>
        <input className="form-input" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name or company…" />
      </div>

      {/* Add form */}
      {showAdd && (
        <SponsorForm title="Add New Sponsor" onSave={addSponsor} onCancel={() => setShowAdd(false)} />
      )}

      {/* Edit form */}
      {editing && (
        <SponsorForm title={`Editing: ${editing.name}`} initial={editing} onSave={updateSponsor} onCancel={() => setEditing(null)} />
      )}

      {/* Table */}
      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem", alignItems: "center" }}><span className="spinner" /> Loading…</div>
      ) : filtered.length > 0 ? (
        <div style={{ overflowX: "auto" }}>
          <table className="hope-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Company</th>
                <th>Email</th>
                <th>WhatsApp</th>
                <th>Notes</th>
                <th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600, color: "#E2E8F0" }}>{s.name}</td>
                  <td>{s.company || "—"}</td>
                  <td>{s.email || "—"}</td>
                  <td>{s.whatsapp || "—"}</td>
                  <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.notes || "—"}</td>
                  <td>
                    <div style={{ display: "flex", gap: "0.4rem" }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => { setEditing(s); setShowAdd(false); }}>✏️</button>
                      <button className="btn btn-danger btn-sm" onClick={() => deleteSponsor(s)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ fontSize: "0.78rem", color: "#64748B", marginTop: "0.5rem" }}>
            {filtered.length} sponsor{filtered.length !== 1 ? "s" : ""} {search ? `matching "${search}"` : "total"}
          </div>
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">👥</div>
          <div className="empty-title">{search ? "No sponsors match your search" : "No sponsors yet"}</div>
          <div className="empty-desc">{search ? "Try a different search term" : 'Click "Add Sponsor" to get started.'}</div>
        </div>
      )}
    </div>
  );
}
