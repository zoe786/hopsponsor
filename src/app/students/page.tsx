"use client";

import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import type { Student, Sponsor, Grade } from "@/lib/types";

export default function StudentsPage() {
  const [students, setStudents]   = useState<Student[]>([]);
  const [sponsors, setSponsors]   = useState<Sponsor[]>([]);
  const [grades, setGrades]       = useState<Grade[]>([]);
  const [search, setSearch]       = useState("");
  const [showAdd, setShowAdd]     = useState(false);
  const [editing, setEditing]     = useState<Student | null>(null);
  const [loading, setLoading]     = useState(true);

  // Form state
  const blank = { name: "", age: 10, contact_info: "", address: "", grade_id: "", sponsor_id: "", auto_send: true, notes: "" };
  const [form, setForm] = useState(blank);

  const setF = (k: string, v: unknown) => setForm((f) => ({ ...f, [k]: v }));

  const load = useCallback(async () => {
    const [sRes, spRes, gRes] = await Promise.all([
      fetch("/api/students").then((r) => r.json()),
      fetch("/api/sponsors").then((r) => r.json()),
      fetch("/api/grades").then((r) => r.json()),
    ]);
    if (sRes.success) setStudents(sRes.data);
    if (spRes.success) setSponsors(spRes.data);
    if (gRes.success) setGrades(gRes.data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = students.filter((s) =>
    !search || [s.name, s.student_code, s.grade_name, s.sponsor_name, s.contact_info].some((v) =>
      (v ?? "").toLowerCase().includes(search.toLowerCase())
    )
  );

  const openAdd = () => { setForm(blank); setEditing(null); setShowAdd(true); };
  const openEdit = (s: Student) => {
    setForm({
      name: s.name, age: s.age, contact_info: s.contact_info ?? "",
      address: s.address ?? "", grade_id: String(s.grade_id ?? ""),
      sponsor_id: String(s.sponsor_id ?? ""), auto_send: Boolean(s.auto_send), notes: s.notes ?? "",
    });
    setEditing(s); setShowAdd(false);
  };

  const saveStudent = async () => {
    const payload = {
      name: form.name, age: Number(form.age), contact_info: form.contact_info,
      address: form.address, grade_id: form.grade_id || null, sponsor_id: form.sponsor_id || null,
      auto_send: form.auto_send, notes: form.notes,
    };
    if (editing) {
      const res = await fetch(`/api/students/${editing.id}`, {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      }).then((r) => r.json());
      if (res.success) { toast.success("Updated!"); setEditing(null); load(); }
      else toast.error(res.error ?? "Failed");
    } else {
      const res = await fetch("/api/students", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      }).then((r) => r.json());
      if (res.success) { toast.success("Student added! Code: " + res.data.student_code); setShowAdd(false); load(); }
      else toast.error(res.error ?? "Failed");
    }
  };

  const deleteStudent = async (s: Student) => {
    if (!confirm(`Delete student "${s.name}"?`)) return;
    const res = await fetch(`/api/students/${s.id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) { toast.success("Deleted"); load(); }
    else toast.error(res.error ?? "Failed");
  };

  const exportCSV = () => {
    const header = ["Code", "Name", "Age", "Grade", "Sponsor", "Contact", "Auto Send", "Notes"];
    const rows = filtered.map((s) => [s.student_code, s.name, s.age, s.grade_name ?? "", s.sponsor_name ?? "", s.contact_info ?? "", s.auto_send ? "Yes" : "No", s.notes ?? ""].map(String));
    const csv = [header, ...rows].map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "students.csv"; a.click();
  };

  const StudentForm = ({ title }: { title: string }) => (
    <div className="hope-card fade-in">
      <div className="section-subheader" style={{ marginTop: 0 }}>{title}</div>
      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Full Name *</label>
          <input className="form-input" value={form.name} onChange={(e) => setF("name", e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">Age</label>
          <input className="form-input" type="number" min={3} max={30} value={form.age} onChange={(e) => setF("age", e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">Contact Info</label>
          <input className="form-input" value={form.contact_info} onChange={(e) => setF("contact_info", e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">Address</label>
          <input className="form-input" value={form.address} onChange={(e) => setF("address", e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">Grade</label>
          <select className="form-select" value={form.grade_id} onChange={(e) => setF("grade_id", e.target.value)}>
            <option value="">— Select grade —</option>
            {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Sponsor</label>
          <select className="form-select" value={form.sponsor_id} onChange={(e) => setF("sponsor_id", e.target.value)}>
            <option value="">— None —</option>
            {sponsors.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
      </div>
      <div className="form-group">
        <label className="form-checkbox">
          <input type="checkbox" checked={form.auto_send} onChange={(e) => setF("auto_send", e.target.checked)} />
          Auto Send Reports
        </label>
      </div>
      <div className="form-group">
        <label className="form-label">Notes</label>
        <textarea className="form-textarea" value={form.notes} onChange={(e) => setF("notes", e.target.value)} rows={2} />
      </div>
      <div style={{ display: "flex", gap: "0.75rem" }}>
        <button className="btn btn-primary" disabled={!form.name.trim()} onClick={saveStudent}>Save</button>
        <button className="btn btn-secondary" onClick={() => { setShowAdd(false); setEditing(null); }}>Cancel</button>
      </div>
    </div>
  );

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Students</div>
          <div className="page-subtitle">Track students and their sponsor assignments</div>
        </div>
        <div style={{ display: "flex", gap: "0.75rem", paddingTop: "0.5rem" }}>
          <button className="btn btn-secondary btn-sm" onClick={exportCSV}>⬇ Export CSV</button>
          <button className="btn btn-primary" onClick={openAdd}>➕ Add Student</button>
        </div>
      </div>

      <div className="search-bar">
        <span className="search-icon">🔍</span>
        <input className="form-input" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search students…" />
      </div>

      {showAdd  && <StudentForm title="Add New Student" />}
      {editing  && <StudentForm title={`Editing: ${editing.name}`} />}

      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem", alignItems: "center" }}><span className="spinner" /> Loading…</div>
      ) : filtered.length > 0 ? (
        <div style={{ overflowX: "auto" }}>
          <table className="hope-table">
            <thead>
              <tr>
                <th>Code</th><th>Name</th><th>Grade</th><th>Sponsor</th><th>Auto Send</th><th>Contact</th><th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr key={s.id}>
                  <td><span className="badge badge-purple">{s.student_code}</span></td>
                  <td style={{ fontWeight: 600, color: "#E2E8F0" }}>{s.name}</td>
                  <td>{s.grade_name || "—"}</td>
                  <td>{s.sponsor_name || "—"}</td>
                  <td>{s.auto_send ? <span className="badge badge-success">✓ Yes</span> : <span className="badge badge-warning">✗ No</span>}</td>
                  <td>{s.contact_info || "—"}</td>
                  <td>
                    <div style={{ display: "flex", gap: "0.4rem" }}>
                      <button className="btn btn-secondary btn-sm" onClick={() => openEdit(s)}>✏️</button>
                      <button className="btn btn-danger btn-sm" onClick={() => deleteStudent(s)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ fontSize: "0.78rem", color: "#64748B", marginTop: "0.5rem" }}>
            {filtered.length} student{filtered.length !== 1 ? "s" : ""} {search ? `matching "${search}"` : "total"}
          </div>
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">🎓</div>
          <div className="empty-title">{search ? "No students match your search" : "No students yet"}</div>
          <div className="empty-desc">{search ? "Try a different search" : 'Click "Add Student" to begin tracking.'}</div>
        </div>
      )}
    </div>
  );
}
