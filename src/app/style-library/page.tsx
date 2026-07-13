"use client";

import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import type { StyleEntry } from "@/lib/types";

export default function StyleLibraryPage() {
  const [styles, setStyles]   = useState<StyleEntry[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({ category: "", message: "", golden_example: false });
  const setF = (k: string, v: unknown) => setForm((f) => ({ ...f, [k]: v }));

  const load = useCallback(() => {
    fetch("/api/styles").then((r) => r.json()).then((d) => {
      if (d.success) setStyles(d.data);
      setLoading(false);
    });
  }, []);

  useEffect(() => { load(); }, [load]);

  const addStyle = async () => {
    const res = await fetch("/api/styles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    }).then((r) => r.json());
    if (res.success) {
      toast.success("✅ Style added!");
      setShowAdd(false);
      setForm({ category: "", message: "", golden_example: false });
      load();
    } else {
      toast.error(res.error ?? "Failed");
    }
  };

  const deleteStyle = async (id: number) => {
    if (!confirm("Delete this style example?")) return;
    const res = await fetch(`/api/styles/${id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) { toast.success("Deleted"); load(); }
    else toast.error(res.error ?? "Failed");
  };

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Style <span className="accent">Library</span></div>
          <div className="page-subtitle">Manage writing style examples used by AI to match your voice</div>
        </div>
        <div style={{ paddingTop: "0.5rem" }}>
          <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
            ➕ Add Style Example
          </button>
        </div>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="hope-card fade-in">
          <div className="section-subheader" style={{ marginTop: 0 }}>Add Style Example</div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <input className="form-input" value={form.category} onChange={(e) => setF("category", e.target.value)} placeholder="e.g. Thank You, Update, Invite…" />
          </div>
          <div className="form-group">
            <label className="form-label">Example Message</label>
            <textarea className="form-textarea" rows={5} value={form.message} onChange={(e) => setF("message", e.target.value)} placeholder="Write an example message in your style…" />
          </div>
          <div className="form-group">
            <label className="form-checkbox">
              <input type="checkbox" checked={form.golden_example} onChange={(e) => setF("golden_example", e.target.checked)} />
              ⭐ Golden Example (reference quality)
            </label>
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button className="btn btn-primary" onClick={addStyle} disabled={!form.category.trim() || !form.message.trim()}>Add Example</button>
            <button className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Style list */}
      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem" }}><span className="spinner" /> Loading…</div>
      ) : styles.length > 0 ? (
        <div>
          {styles.map((s) => (
            <div key={s.id} className="hope-card fade-in" style={{ position: "relative" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span className="badge badge-purple">{s.category}</span>
                  {s.golden_example ? <span className="badge badge-warning">⭐ Golden</span> : null}
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => deleteStyle(s.id)} style={{ marginLeft: "0.5rem" }}>🗑️</button>
              </div>
              <div style={{ color: "#94A3B8", fontSize: "0.875rem", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
                {s.message}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">🎨</div>
          <div className="empty-title">No style examples yet</div>
          <div className="empty-desc">Add examples to help AI match your writing voice.</div>
        </div>
      )}
    </div>
  );
}
