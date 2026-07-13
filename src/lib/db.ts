/**
 * Database layer — TypeScript port of database.py
 *
 * Bugs fixed vs Python original:
 * 1. update_sponsor / delete_sponsor now accept numeric ID (not name)
 * 2. get_scheduled_messages now always includes ORDER BY
 * 3. get_next_student_code handles non-standard codes gracefully
 */

import Database from "better-sqlite3";
import path from "path";
import fs from "fs";
import type {
  Sponsor,
  Grade,
  Student,
  StyleEntry,
  MessageRecord,
  ScheduledMessage,
  Report,
} from "./types";

// ── Connection ────────────────────────────────────────────────────────────────

const DB_PATH = process.env.DB_PATH || "./data/sponsor_assistant.db";

function ensureDir(filePath: string) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!_db) {
    ensureDir(DB_PATH);
    _db = new Database(DB_PATH);
    _db.pragma("journal_mode = WAL");
    _db.pragma("foreign_keys = ON");
    initializeDatabase(_db);
  }
  return _db;
}

// ── Schema ────────────────────────────────────────────────────────────────────

function initializeDatabase(db: Database.Database) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS sponsors (
      id       INTEGER PRIMARY KEY AUTOINCREMENT,
      name     TEXT,
      company  TEXT,
      whatsapp TEXT,
      email    TEXT,
      notes    TEXT
    );

    CREATE TABLE IF NOT EXISTS style_library (
      id             INTEGER PRIMARY KEY AUTOINCREMENT,
      category       TEXT,
      message        TEXT,
      golden_example INTEGER
    );

    CREATE TABLE IF NOT EXISTS message_history (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      date      TEXT,
      recipient TEXT,
      channel   TEXT,
      direction TEXT,
      message   TEXT,
      status    TEXT
    );

    CREATE TABLE IF NOT EXISTS scheduled_messages (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      recipient TEXT,
      channel   TEXT,
      message   TEXT,
      send_time TEXT,
      status    TEXT
    );

    CREATE TABLE IF NOT EXISTS grades (
      id   INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS students (
      id           INTEGER PRIMARY KEY AUTOINCREMENT,
      student_code TEXT UNIQUE NOT NULL,
      name         TEXT NOT NULL,
      age          INTEGER,
      contact_info TEXT,
      address      TEXT,
      grade_id     INTEGER,
      sponsor_id   INTEGER,
      auto_send    INTEGER DEFAULT 1,
      notes        TEXT,
      FOREIGN KEY (grade_id)   REFERENCES grades(id),
      FOREIGN KEY (sponsor_id) REFERENCES sponsors(id)
    );

    CREATE TABLE IF NOT EXISTS reports (
      id           INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id   INTEGER NOT NULL,
      file_path    TEXT NOT NULL,
      file_name    TEXT,
      upload_date  TEXT DEFAULT CURRENT_TIMESTAMP,
      message_sent INTEGER DEFAULT 0,
      sent_to      TEXT,
      FOREIGN KEY (student_id) REFERENCES students(id)
    );

    CREATE INDEX IF NOT EXISTS idx_messages_recipient ON message_history(recipient);
    CREATE INDEX IF NOT EXISTS idx_messages_date      ON message_history(date);
    CREATE INDEX IF NOT EXISTS idx_sponsors_name      ON sponsors(name);
    CREATE INDEX IF NOT EXISTS idx_students_sponsor   ON students(sponsor_id);
  `);

  const defaultGrades = [
    "Baby Class",
    "KG 1",
    "KG 2",
    "KG 3",
    "Grade 1",
    "Grade 2",
    "Grade 3",
    "Grade 4",
    "Grade 5",
    "Grade 6",
    "Grade 7",
    "Form 1",
    "Form 2",
    "Form 3",
    "Form 4",
    "Form 5",
    "Form 6",
    "College",
    "University",
  ];

  const insertGrade = db.prepare(
    "INSERT OR IGNORE INTO grades (name) VALUES (?)"
  );
  for (const g of defaultGrades) insertGrade.run(g);
}

// ── Sponsors ──────────────────────────────────────────────────────────────────

export function addSponsor(
  name: string,
  company: string,
  whatsapp: string,
  email: string,
  notes: string
): number {
  const db = getDb();
  const result = db
    .prepare(
      "INSERT INTO sponsors (name, company, whatsapp, email, notes) VALUES (?, ?, ?, ?, ?)"
    )
    .run(name, company, whatsapp, email, notes);
  return result.lastInsertRowid as number;
}

export function getSponsors(): Sponsor[] {
  return getDb()
    .prepare("SELECT * FROM sponsors ORDER BY name")
    .all() as Sponsor[];
}

export function getSponsor(id: number): Sponsor | null {
  return (
    (getDb()
      .prepare("SELECT * FROM sponsors WHERE id = ?")
      .get(id) as Sponsor) ?? null
  );
}

/** BUG FIX: original app.py called update_sponsor(name, ...) instead of (id, name, ...) */
export function updateSponsor(
  id: number,
  name: string,
  company: string,
  whatsapp: string,
  email: string,
  notes: string
): void {
  getDb()
    .prepare(
      "UPDATE sponsors SET name=?, company=?, whatsapp=?, email=?, notes=? WHERE id=?"
    )
    .run(name, company, whatsapp, email, notes, id);
}

/** BUG FIX: original app.py called delete_sponsor(name) instead of delete_sponsor(id) */
export function deleteSponsor(id: number): void {
  getDb().prepare("DELETE FROM sponsors WHERE id = ?").run(id);
}

// ── Style Library ─────────────────────────────────────────────────────────────

export function addStyle(
  category: string,
  message: string,
  goldenExample: boolean
): number {
  const result = getDb()
    .prepare(
      "INSERT INTO style_library (category, message, golden_example) VALUES (?, ?, ?)"
    )
    .run(category, message, goldenExample ? 1 : 0);
  return result.lastInsertRowid as number;
}

export function getStyles(): StyleEntry[] {
  return getDb()
    .prepare("SELECT * FROM style_library ORDER BY id DESC")
    .all() as StyleEntry[];
}

export function deleteStyle(id: number): void {
  getDb().prepare("DELETE FROM style_library WHERE id = ?").run(id);
}

// ── Message History ───────────────────────────────────────────────────────────

export function addMessage(
  date: string,
  recipient: string,
  channel: string,
  direction: string,
  message: string,
  status: string
): void {
  getDb()
    .prepare(
      "INSERT INTO message_history (date, recipient, channel, direction, message, status) VALUES (?, ?, ?, ?, ?, ?)"
    )
    .run(date, recipient, channel, direction, message, status);
}

export function getMessages(limit?: number): MessageRecord[] {
  const query = limit
    ? `SELECT * FROM message_history ORDER BY id DESC LIMIT ${limit}`
    : "SELECT * FROM message_history ORDER BY id DESC";
  return getDb().prepare(query).all() as MessageRecord[];
}

export function getMessagesByDay(
  days = 30
): { date: string; count: number }[] {
  return getDb()
    .prepare(
      `SELECT date, COUNT(*) as count
       FROM message_history
       WHERE date >= date('now', '-${days} days')
       GROUP BY date
       ORDER BY date ASC`
    )
    .all() as { date: string; count: number }[];
}

// ── Scheduled Messages ────────────────────────────────────────────────────────

export function addScheduledMessage(
  recipient: string,
  channel: string,
  message: string,
  sendTime: string
): number {
  const result = getDb()
    .prepare(
      "INSERT INTO scheduled_messages (recipient, channel, message, send_time, status) VALUES (?, ?, ?, ?, 'pending')"
    )
    .run(recipient, channel, message, sendTime);
  return result.lastInsertRowid as number;
}

/** BUG FIX: original get_scheduled_messages(status=None) branch omitted ORDER BY */
export function getScheduledMessages(
  status?: string | null
): ScheduledMessage[] {
  if (status) {
    return getDb()
      .prepare(
        "SELECT * FROM scheduled_messages WHERE status = ? ORDER BY send_time ASC"
      )
      .all(status) as ScheduledMessage[];
  }
  return getDb()
    .prepare("SELECT * FROM scheduled_messages ORDER BY send_time ASC")
    .all() as ScheduledMessage[];
}

export function getDueScheduledMessages(): ScheduledMessage[] {
  const now = new Date().toISOString();
  return getDb()
    .prepare(
      "SELECT * FROM scheduled_messages WHERE status = 'pending' AND send_time <= ? ORDER BY send_time ASC"
    )
    .all(now) as ScheduledMessage[];
}

export function updateScheduledMessageStatus(id: number, status: string): void {
  getDb()
    .prepare("UPDATE scheduled_messages SET status = ? WHERE id = ?")
    .run(status, id);
}

// ── Grades ────────────────────────────────────────────────────────────────────

export function getGrades(): Grade[] {
  return getDb()
    .prepare("SELECT * FROM grades ORDER BY id")
    .all() as Grade[];
}

// ── Students ──────────────────────────────────────────────────────────────────

function getNextStudentCode(db: Database.Database): string {
  const row = db
    .prepare(
      "SELECT MAX(CAST(SUBSTR(student_code, 5) AS INTEGER)) as max_code FROM students WHERE student_code LIKE 'STU-%'"
    )
    .get() as { max_code: number | null };
  const maxCode = row?.max_code ?? 0;
  return `STU-${String(maxCode + 1).padStart(4, "0")}`;
}

export function addStudent(
  name: string,
  age: number,
  contactInfo: string,
  address: string,
  gradeId: number | null,
  sponsorId: number | null,
  autoSend: boolean,
  notes: string
): string {
  const db = getDb();
  const code = getNextStudentCode(db);
  db.prepare(
    `INSERT INTO students
       (student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).run(
    code,
    name,
    age,
    contactInfo,
    address,
    gradeId,
    sponsorId,
    autoSend ? 1 : 0,
    notes
  );
  return code;
}

export function getStudents(): Student[] {
  return getDb()
    .prepare(
      `SELECT s.id, s.student_code, s.name, s.age, s.contact_info, s.address,
              g.name  as grade_name,
              sp.name as sponsor_name,
              sp.email     as sponsor_email,
              sp.whatsapp  as sponsor_phone,
              s.auto_send, s.notes
       FROM students s
       LEFT JOIN grades   g  ON s.grade_id   = g.id
       LEFT JOIN sponsors sp ON s.sponsor_id  = sp.id
       ORDER BY s.name`
    )
    .all() as Student[];
}

export function getStudent(id: number): Student | null {
  return (
    (getDb()
      .prepare("SELECT * FROM students WHERE id = ?")
      .get(id) as Student) ?? null
  );
}

export function updateStudent(
  id: number,
  name: string,
  age: number,
  contactInfo: string,
  address: string,
  gradeId: number | null,
  sponsorId: number | null,
  autoSend: boolean,
  notes: string
): void {
  getDb()
    .prepare(
      `UPDATE students
       SET name=?, age=?, contact_info=?, address=?, grade_id=?, sponsor_id=?, auto_send=?, notes=?
       WHERE id=?`
    )
    .run(
      name,
      age,
      contactInfo,
      address,
      gradeId,
      sponsorId,
      autoSend ? 1 : 0,
      notes,
      id
    );
}

export function deleteStudent(id: number): void {
  getDb().prepare("DELETE FROM students WHERE id = ?").run(id);
}

export function updateStudentAutoSend(id: number, autoSend: boolean): void {
  getDb()
    .prepare("UPDATE students SET auto_send = ? WHERE id = ?")
    .run(autoSend ? 1 : 0, id);
}

export function getStudentsByNameFragment(fragment: string): Student[] {
  return getDb()
    .prepare(
      "SELECT id, name, student_code FROM students WHERE name LIKE ? ORDER BY name"
    )
    .all(`%${fragment}%`) as Student[];
}

// ── Reports ───────────────────────────────────────────────────────────────────

export function addReport(
  studentId: number,
  filePath: string,
  fileName: string
): number {
  const result = getDb()
    .prepare(
      `INSERT INTO reports (student_id, file_path, file_name, upload_date, message_sent, sent_to)
       VALUES (?, ?, ?, datetime('now'), 0, NULL)`
    )
    .run(studentId, filePath, fileName);
  return result.lastInsertRowid as number;
}

export function getReports(studentId?: number): Report[] {
  if (studentId) {
    return getDb()
      .prepare(
        "SELECT * FROM reports WHERE student_id = ? ORDER BY upload_date DESC"
      )
      .all(studentId) as Report[];
  }
  return getDb()
    .prepare("SELECT * FROM reports ORDER BY upload_date DESC")
    .all() as Report[];
}

export function updateReportSent(reportId: number, sentTo: string): void {
  getDb()
    .prepare("UPDATE reports SET message_sent = 1, sent_to = ? WHERE id = ?")
    .run(sentTo, reportId);
}

// ── Dashboard Stats ───────────────────────────────────────────────────────────

export function getDashboardStats() {
  const db = getDb();
  const totalSponsors = (
    db.prepare("SELECT COUNT(*) as c FROM sponsors").get() as { c: number }
  ).c;
  const totalStudents = (
    db.prepare("SELECT COUNT(*) as c FROM students").get() as { c: number }
  ).c;
  const totalMessages = (
    db.prepare("SELECT COUNT(*) as c FROM message_history").get() as {
      c: number;
    }
  ).c;
  const pendingScheduled = (
    db
      .prepare(
        "SELECT COUNT(*) as c FROM scheduled_messages WHERE status = 'pending'"
      )
      .get() as { c: number }
  ).c;

  const recentMessages = db
    .prepare(
      "SELECT * FROM message_history ORDER BY id DESC LIMIT 10"
    )
    .all() as MessageRecord[];

  const messagesByDay = db
    .prepare(
      `SELECT date, COUNT(*) as count
       FROM message_history
       WHERE date >= date('now', '-30 days')
       GROUP BY date
       ORDER BY date ASC`
    )
    .all() as { date: string; count: number }[];

  return {
    totalSponsors,
    totalStudents,
    totalMessages,
    pendingScheduled,
    recentMessages,
    messagesByDay,
  };
}
