"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import type { Report } from "@/lib/types";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [autoMatch, setAutoMatch] = useState(true);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const load = useCallback(() => {
    fetch("/api/reports")
      .then((r) => r.json())
      .then((d) => { if (d.success) setReports(d.data); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    setSelectedFiles(files);
  };

  const uploadFiles = async () => {
    if (!selectedFiles.length) { toast.error("Select at least one file"); return; }
    setUploading(true);
    const fd = new FormData();
    for (const f of selectedFiles) fd.append("files", f);
    fd.append("auto_match", String(autoMatch));

    const res = await fetch("/api/reports", { method: "POST", body: fd }).then((r) => r.json());
    setUploading(false);

    if (res.success) {
      const matched = (res.data as { studentName: string | null }[]).filter((r) => r.studentName).length;
      const total = (res.data as unknown[]).length;
      toast.success(`✅ Uploaded ${total} file(s), matched ${matched} to students`);
      setSelectedFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = "";
      load();
    } else {
      toast.error(res.error ?? "Upload failed");
    }
  };

  const deleteReport = async (id: number) => {
    if (!confirm("Delete this report?")) return;
    const res = await fetch(`/api/reports/${id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) { toast.success("Deleted"); load(); }
    else toast.error(res.error ?? "Failed");
  };

  const markSent = async (id: number, sentTo: string) => {
    const res = await fetch(`/api/reports/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sent_to: sentTo }),
    }).then((r) => r.json());
    if (res.success) { toast.success("Marked as sent"); load(); }
    else toast.error(res.error ?? "Failed");
  };

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Student <span className="accent">Reports</span></div>
          <div className="page-subtitle">Upload and manage student report files</div>
        </div>
      </div>

      {/* Upload card */}
      <div className="hope-card fade-in" style={{ marginBottom: "1.5rem" }}>
        <div className="section-subheader" style={{ marginTop: 0 }}>📤 Upload Reports</div>
        <div className="form-group">
          <label className="form-label">Select files (PDF, images, documents)</label>
          <label
            className="file-upload-area"
            style={{ display: "block", cursor: "pointer", padding: "1.25rem", textAlign: "center" }}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
            {selectedFiles.length > 0 ? (
              <div style={{ color: "#C4B5FD" }}>
                📎 {selectedFiles.length} file{selectedFiles.length !== 1 ? "s" : ""} selected:{" "}
                {selectedFiles.map((f) => f.name).join(", ")}
              </div>
            ) : (
              <div style={{ color: "#64748B", fontSize: "0.875rem" }}>
                Click to select report files
              </div>
            )}
          </label>
        </div>

        <div className="form-group">
          <label className="form-checkbox">
            <input
              type="checkbox"
              checked={autoMatch}
              onChange={(e) => setAutoMatch(e.target.checked)}
            />
            🤖 Auto-match files to students using AI
          </label>
        </div>

        <button
          className="btn btn-primary"
          onClick={uploadFiles}
          disabled={uploading || !selectedFiles.length}
        >
          {uploading ? <><span className="spinner" /> Uploading…</> : "📤 Upload"}
        </button>
      </div>

      {/* Reports list */}
      <div className="section-subheader">📁 Uploaded Reports ({reports.length})</div>

      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span className="spinner" /> Loading…
        </div>
      ) : reports.length > 0 ? (
        <div className="hope-card" style={{ overflowX: "auto" }}>
          <table className="hope-table">
            <thead>
              <tr>
                <th>File</th>
                <th>Student</th>
                <th>Uploaded</th>
                <th>Sent</th>
                <th style={{ width: 140 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 600, color: "#E2E8F0" }}>{r.file_name || r.file_path}</td>
                  <td>{r.student_name || <span style={{ color: "#64748B" }}>—</span>}</td>
                  <td style={{ fontSize: "0.82rem" }}>{r.upload_date ? r.upload_date.slice(0, 10) : "—"}</td>
                  <td>
                    {r.message_sent ? (
                      <span className="badge badge-success">✓ Sent{r.sent_to ? ` to ${r.sent_to}` : ""}</span>
                    ) : (
                      <span className="badge badge-warning">Unsent</span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: "0.4rem" }}>
                      {!r.message_sent && r.student_name && (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => {
                            const to = prompt("Mark as sent to (enter email or name):", r.student_name ?? "");
                            if (to) markSent(r.id, to);
                          }}
                        >
                          ✉️
                        </button>
                      )}
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => deleteReport(r.id)}
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">📁</div>
          <div className="empty-title">No reports uploaded yet</div>
          <div className="empty-desc">Upload student report files to track and send them to sponsors.</div>
        </div>
      )}
    </div>
  );
}
