"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import type { PaymentCommitment, Sponsor, Student } from "@/lib/types";

const blankForm = {
  sponsor_id: "",
  student_id: "",
  amount_committed: "",
  amount_received: "0",
  currency: "USD",
  frequency: "Monthly",
  commitment_date: new Date().toISOString().split("T")[0],
  next_due_date: "",
  last_payment_date: "",
  status: "active",
  notes: "",
};

export default function PaymentsPage() {
  const [items, setItems] = useState<PaymentCommitment[]>([]);
  const [sponsors, setSponsors] = useState<Sponsor[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [form, setForm] = useState(blankForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const setF = (key: string, value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  const load = useCallback(async () => {
    const [itemsRes, sponsorsRes, studentsRes] = await Promise.all([
      fetch("/api/payment-commitments").then((r) => r.json()),
      fetch("/api/sponsors").then((r) => r.json()),
      fetch("/api/students").then((r) => r.json()),
    ]);
    if (itemsRes.success) setItems(itemsRes.data);
    if (sponsorsRes.success) setSponsors(sponsorsRes.data);
    if (studentsRes.success) setStudents(studentsRes.data);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const totalCommitted = useMemo(() => items.reduce((sum, item) => sum + Number(item.amount_committed || 0), 0), [items]);
  const totalReceived = useMemo(() => items.reduce((sum, item) => sum + Number(item.amount_received || 0), 0), [items]);

  const reset = () => {
    setForm(blankForm);
    setEditingId(null);
  };

  const save = async () => {
    const payload = {
      ...form,
      sponsor_id: Number(form.sponsor_id),
      student_id: form.student_id ? Number(form.student_id) : null,
      amount_committed: Number(form.amount_committed),
      amount_received: Number(form.amount_received),
      next_due_date: form.next_due_date || null,
      last_payment_date: form.last_payment_date || null,
    };

    const url = editingId ? `/api/payment-commitments/${editingId}` : "/api/payment-commitments";
    const method = editingId ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => r.json());

    if (res.success) {
      toast.success(editingId ? "Commitment updated" : "Commitment added");
      reset();
      load();
    } else {
      toast.error(res.error ?? "Failed");
    }
  };

  const edit = (item: PaymentCommitment) => {
    setEditingId(item.id);
    setForm({
      sponsor_id: String(item.sponsor_id),
      student_id: item.student_id ? String(item.student_id) : "",
      amount_committed: String(item.amount_committed),
      amount_received: String(item.amount_received),
      currency: item.currency,
      frequency: item.frequency,
      commitment_date: item.commitment_date,
      next_due_date: item.next_due_date ?? "",
      last_payment_date: item.last_payment_date ?? "",
      status: item.status,
      notes: item.notes ?? "",
    });
  };

  const remove = async (item: PaymentCommitment) => {
    if (!confirm(`Delete commitment for ${item.sponsor_name}?`)) return;
    const res = await fetch(`/api/payment-commitments/${item.id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) {
      toast.success("Deleted");
      load();
    } else toast.error(res.error ?? "Failed");
  };

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Payment <span className="accent">Commitments</span></div>
          <div className="page-subtitle">Track sponsor promises, amounts received, and upcoming due dates</div>
        </div>
      </div>

      <div className="stat-grid" style={{ marginBottom: "1.5rem" }}>
        <div className="stat-card fade-in"><div className="stat-icon">💵</div><div className="stat-value">{totalCommitted.toFixed(2)}</div><div className="stat-label">Committed</div></div>
        <div className="stat-card fade-in"><div className="stat-icon">✅</div><div className="stat-value">{totalReceived.toFixed(2)}</div><div className="stat-label">Received</div></div>
        <div className="stat-card fade-in"><div className="stat-icon">⏳</div><div className="stat-value">{(totalCommitted - totalReceived).toFixed(2)}</div><div className="stat-label">Outstanding</div></div>
      </div>

      <div className="hope-card fade-in">
        <div className="section-subheader" style={{ marginTop: 0 }}>{editingId ? "Edit commitment" : "Add commitment"}</div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Sponsor *</label>
            <select className="form-select" value={form.sponsor_id} onChange={(e) => setF("sponsor_id", e.target.value)}>
              <option value="">— Select sponsor —</option>
              {sponsors.map((sponsor) => <option key={sponsor.id} value={sponsor.id}>{sponsor.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Student</label>
            <select className="form-select" value={form.student_id} onChange={(e) => setF("student_id", e.target.value)}>
              <option value="">— Optional —</option>
              {students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Committed Amount *</label>
            <input className="form-input" type="number" min="0" step="0.01" value={form.amount_committed} onChange={(e) => setF("amount_committed", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Received Amount</label>
            <input className="form-input" type="number" min="0" step="0.01" value={form.amount_received} onChange={(e) => setF("amount_received", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Currency</label>
            <input className="form-input" value={form.currency} onChange={(e) => setF("currency", e.target.value.toUpperCase())} maxLength={6} />
          </div>
          <div className="form-group">
            <label className="form-label">Frequency *</label>
            <select className="form-select" value={form.frequency} onChange={(e) => setF("frequency", e.target.value)}>
              <option>Monthly</option>
              <option>Quarterly</option>
              <option>Yearly</option>
              <option>One-time</option>
              <option>Custom</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Commitment Date *</label>
            <input className="form-input" type="date" value={form.commitment_date} onChange={(e) => setF("commitment_date", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Next Due Date</label>
            <input className="form-input" type="date" value={form.next_due_date} onChange={(e) => setF("next_due_date", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Last Payment Date</label>
            <input className="form-input" type="date" value={form.last_payment_date} onChange={(e) => setF("last_payment_date", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Status</label>
            <select className="form-select" value={form.status} onChange={(e) => setF("status", e.target.value)}>
              <option value="active">Active</option>
              <option value="overdue">Overdue</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
        <div className="form-group">
          <label className="form-label">Notes</label>
          <textarea className="form-textarea" rows={3} value={form.notes} onChange={(e) => setF("notes", e.target.value)} />
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button className="btn btn-primary" onClick={save} disabled={!form.sponsor_id || !form.amount_committed}>Save Commitment</button>
          {editingId && <button className="btn btn-secondary" onClick={reset}>Cancel</button>}
        </div>
      </div>

      <div className="section-subheader">Tracked commitments</div>
      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem" }}><span className="spinner" /> Loading…</div>
      ) : items.length > 0 ? (
        <div className="hope-card" style={{ overflowX: "auto" }}>
          <table className="hope-table">
            <thead>
              <tr>
                <th>Sponsor</th>
                <th>Student</th>
                <th>Amount</th>
                <th>Received</th>
                <th>Frequency</th>
                <th>Next Due</th>
                <th>Status</th>
                <th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.sponsor_name}</td>
                  <td>{item.student_name || "—"}</td>
                  <td>{item.currency} {Number(item.amount_committed).toFixed(2)}</td>
                  <td>{item.currency} {Number(item.amount_received).toFixed(2)}</td>
                  <td>{item.frequency}</td>
                  <td>{item.next_due_date || "—"}</td>
                  <td><span className={`badge ${item.status === "completed" ? "badge-success" : item.status === "overdue" ? "badge-danger" : "badge-warning"}`}>{item.status}</span></td>
                  <td>
                    <div style={{ display: "flex", gap: "0.4rem" }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => edit(item)}>✏️</button>
                      <button className="btn btn-danger btn-sm" onClick={() => remove(item)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">💳</div>
          <div className="empty-title">No commitments yet</div>
          <div className="empty-desc">Add a sponsor commitment to start tracking incoming payments.</div>
        </div>
      )}
    </div>
  );
}
