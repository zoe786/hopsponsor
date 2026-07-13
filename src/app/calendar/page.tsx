"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import type { CalendarEvent, Sponsor, Student } from "@/lib/types";

const blankForm = {
  title: "",
  description: "",
  start_date: new Date().toISOString().split("T")[0],
  start_time: "09:00",
  end_date: new Date().toISOString().split("T")[0],
  end_time: "10:00",
  location: "",
  sponsor_id: "",
  student_id: "",
};

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [sponsors, setSponsors] = useState<Sponsor[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [form, setForm] = useState(blankForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const setF = (key: string, value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  const load = useCallback(async () => {
    const [eventsRes, sponsorsRes, studentsRes] = await Promise.all([
      fetch("/api/calendar-events").then((r) => r.json()),
      fetch("/api/sponsors").then((r) => r.json()),
      fetch("/api/students").then((r) => r.json()),
    ]);
    if (eventsRes.success) setEvents(eventsRes.data);
    if (sponsorsRes.success) setSponsors(sponsorsRes.data);
    if (studentsRes.success) setStudents(studentsRes.data);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const feedUrl = useMemo(() => (typeof window === "undefined" ? "" : `${window.location.origin}/api/calendar/feed`), []);

  const reset = () => {
    setForm(blankForm);
    setEditingId(null);
  };

  const save = async () => {
    const start = new Date(`${form.start_date}T${form.start_time}`).toISOString();
    const end = new Date(`${form.end_date}T${form.end_time}`).toISOString();
    const payload = {
      title: form.title,
      description: form.description,
      start_time: start,
      end_time: end,
      location: form.location,
      sponsor_id: form.sponsor_id ? Number(form.sponsor_id) : null,
      student_id: form.student_id ? Number(form.student_id) : null,
      source: editingId ? "manual" : "manual",
    };
    const res = await fetch(editingId ? `/api/calendar-events/${editingId}` : "/api/calendar-events", {
      method: editingId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => r.json());

    if (res.success) {
      toast.success(editingId ? "Event updated" : "Event added");
      reset();
      load();
    } else {
      toast.error(res.error ?? "Failed");
    }
  };

  const edit = (event: CalendarEvent) => {
    const start = new Date(event.start_time);
    const end = new Date(event.end_time || event.start_time);
    setEditingId(event.id);
    setForm({
      title: event.title,
      description: event.description ?? "",
      start_date: start.toISOString().split("T")[0],
      start_time: start.toISOString().slice(11, 16),
      end_date: end.toISOString().split("T")[0],
      end_time: end.toISOString().slice(11, 16),
      location: event.location ?? "",
      sponsor_id: event.sponsor_id ? String(event.sponsor_id) : "",
      student_id: event.student_id ? String(event.student_id) : "",
    });
  };

  const remove = async (event: CalendarEvent) => {
    if (!confirm(`Delete event '${event.title}'?`)) return;
    const res = await fetch(`/api/calendar-events/${event.id}`, { method: "DELETE" }).then((r) => r.json());
    if (res.success) {
      toast.success("Deleted");
      load();
    } else toast.error(res.error ?? "Failed");
  };

  return (
    <div className="fade-in">
      <div className="page-header-row">
        <div>
          <div className="page-title">Shared <span className="accent">Calendar</span></div>
          <div className="page-subtitle">Track events, follow-ups, and export an iCalendar feed that Google Calendar and other apps can import</div>
        </div>
      </div>

      <div className="hope-card fade-in" style={{ marginBottom: "1rem" }}>
        <div className="section-subheader" style={{ marginTop: 0 }}>Calendar sync</div>
        <div style={{ color: "#94A3B8", fontSize: "0.9rem", lineHeight: 1.6 }}>
          Use the ICS feed below in Google Calendar, Apple Calendar, Outlook, or any other calendar app that supports iCalendar subscriptions.
        </div>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginTop: "0.75rem", flexWrap: "wrap" }}>
          <code style={{ background: "rgba(255,255,255,0.04)", padding: "0.5rem 0.75rem", borderRadius: 8 }}>{feedUrl || "/api/calendar/feed"}</code>
          <a className="btn btn-secondary btn-sm" href="/api/calendar/feed" target="_blank" rel="noreferrer">Download .ics</a>
          <button className="btn btn-secondary btn-sm" onClick={() => navigator.clipboard.writeText(feedUrl).then(() => toast.success("Feed URL copied"))}>Copy Feed URL</button>
        </div>
      </div>

      <div className="hope-card fade-in">
        <div className="section-subheader" style={{ marginTop: 0 }}>{editingId ? "Edit event" : "Add calendar event"}</div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Title *</label>
            <input className="form-input" value={form.title} onChange={(e) => setF("title", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Location</label>
            <input className="form-input" value={form.location} onChange={(e) => setF("location", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Start Date</label>
            <input className="form-input" type="date" value={form.start_date} onChange={(e) => setF("start_date", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Start Time</label>
            <input className="form-input" type="time" value={form.start_time} onChange={(e) => setF("start_time", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">End Date</label>
            <input className="form-input" type="date" value={form.end_date} onChange={(e) => setF("end_date", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">End Time</label>
            <input className="form-input" type="time" value={form.end_time} onChange={(e) => setF("end_time", e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Sponsor</label>
            <select className="form-select" value={form.sponsor_id} onChange={(e) => setF("sponsor_id", e.target.value)}>
              <option value="">— Optional —</option>
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
        </div>
        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea className="form-textarea" rows={3} value={form.description} onChange={(e) => setF("description", e.target.value)} />
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button className="btn btn-primary" onClick={save} disabled={!form.title.trim()}>Save Event</button>
          {editingId && <button className="btn btn-secondary" onClick={reset}>Cancel</button>}
        </div>
      </div>

      <div className="section-subheader">Upcoming events</div>
      {loading ? (
        <div style={{ color: "#64748B", display: "flex", gap: "0.5rem" }}><span className="spinner" /> Loading…</div>
      ) : events.length > 0 ? (
        <div className="hope-card">
          {events.map((event) => (
            <div className="activity-row" key={event.id}>
              <div className="activity-left" style={{ flex: 1 }}>
                <div className="activity-avatar">📅</div>
                <div>
                  <div className="activity-name">{event.title}</div>
                  <div className="activity-excerpt">{event.description || event.location || "No details"}</div>
                  <div className="activity-meta">{new Date(event.start_time).toLocaleString()} {event.end_time ? `→ ${new Date(event.end_time).toLocaleString()}` : ""}</div>
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
                {event.sponsor_name ? <span className="badge badge-purple">{event.sponsor_name}</span> : null}
                {event.student_name ? <span className="badge badge-success">{event.student_name}</span> : null}
                <button className="btn btn-secondary btn-sm" onClick={() => edit(event)}>✏️</button>
                <button className="btn btn-danger btn-sm" onClick={() => remove(event)}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="hope-card empty-state">
          <div className="empty-icon">📅</div>
          <div className="empty-title">No calendar events yet</div>
          <div className="empty-desc">Create an event or subscribe to the ICS feed after you add one.</div>
        </div>
      )}
    </div>
  );
}
