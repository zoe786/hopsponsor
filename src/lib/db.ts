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
  PaymentCommitment,
  CalendarEvent,
} from "./types";

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

function hasColumn(db: Database.Database, table: string, column: string): boolean {
  const allowedTables = new Set([
    "scheduled_messages",
    "sponsors",
    "style_library",
    "message_history",
    "grades",
    "students",
    "reports",
    "payment_commitments",
    "calendar_events",
  ]);
  if (!allowedTables.has(table)) {
    throw new Error(`Unsupported table for schema inspection: ${table}`);
  }
  const columns = db.prepare(`PRAGMA table_info(${table})`).all() as { name: string }[];
  return columns.some((entry) => entry.name === column);
}

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
      id           INTEGER PRIMARY KEY AUTOINCREMENT,
      recipient    TEXT,
      recipient_id INTEGER,
      channel      TEXT,
      subject      TEXT DEFAULT '',
      message      TEXT,
      send_time    TEXT,
      status       TEXT,
      FOREIGN KEY (recipient_id) REFERENCES sponsors(id) ON DELETE SET NULL
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
      FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS reports (
      id           INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id   INTEGER NOT NULL,
      file_path    TEXT NOT NULL,
      file_name    TEXT,
      upload_date  TEXT DEFAULT CURRENT_TIMESTAMP,
      message_sent INTEGER DEFAULT 0,
      sent_to      TEXT,
      FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS payment_commitments (
      id                INTEGER PRIMARY KEY AUTOINCREMENT,
      sponsor_id        INTEGER NOT NULL,
      student_id        INTEGER,
      amount_committed  REAL NOT NULL,
      amount_received   REAL DEFAULT 0,
      currency          TEXT DEFAULT 'USD',
      frequency         TEXT NOT NULL,
      commitment_date   TEXT NOT NULL,
      next_due_date     TEXT,
      last_payment_date TEXT,
      status            TEXT DEFAULT 'active',
      notes             TEXT DEFAULT '',
      FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) ON DELETE CASCADE,
      FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS calendar_events (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      title       TEXT NOT NULL,
      description TEXT DEFAULT '',
      start_time  TEXT NOT NULL,
      end_time    TEXT,
      location    TEXT DEFAULT '',
      sponsor_id  INTEGER,
      student_id  INTEGER,
      source      TEXT DEFAULT 'manual',
      FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) ON DELETE SET NULL,
      FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
    );

    CREATE INDEX IF NOT EXISTS idx_messages_recipient       ON message_history(recipient);
    CREATE INDEX IF NOT EXISTS idx_messages_date            ON message_history(date);
    CREATE INDEX IF NOT EXISTS idx_sponsors_name            ON sponsors(name);
    CREATE INDEX IF NOT EXISTS idx_students_sponsor         ON students(sponsor_id);
    CREATE INDEX IF NOT EXISTS idx_scheduled_messages_time  ON scheduled_messages(send_time);
    CREATE INDEX IF NOT EXISTS idx_scheduled_messages_state ON scheduled_messages(status);
    CREATE INDEX IF NOT EXISTS idx_reports_student          ON reports(student_id);
    CREATE INDEX IF NOT EXISTS idx_payments_sponsor         ON payment_commitments(sponsor_id);
    CREATE INDEX IF NOT EXISTS idx_payments_next_due        ON payment_commitments(next_due_date);
    CREATE INDEX IF NOT EXISTS idx_calendar_start_time      ON calendar_events(start_time);
  `);

  if (!hasColumn(db, "scheduled_messages", "recipient_id")) {
    db.exec("ALTER TABLE scheduled_messages ADD COLUMN recipient_id INTEGER");
  }
  if (!hasColumn(db, "scheduled_messages", "subject")) {
    db.exec("ALTER TABLE scheduled_messages ADD COLUMN subject TEXT DEFAULT ''");
  }

  const defaultGrades = [
    "No Class",
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

  const insertGrade = db.prepare("INSERT OR IGNORE INTO grades (name) VALUES (?)");
  for (const g of defaultGrades) insertGrade.run(g);
}

export function addSponsor(
  name: string,
  company: string,
  whatsapp: string,
  email: string,
  notes: string
): number {
  const result = getDb()
    .prepare(
      "INSERT INTO sponsors (name, company, whatsapp, email, notes) VALUES (?, ?, ?, ?, ?)"
    )
    .run(name, company, whatsapp, email, notes);
  return result.lastInsertRowid as number;
}

export function getSponsors(): Sponsor[] {
  return getDb().prepare("SELECT * FROM sponsors ORDER BY name").all() as Sponsor[];
}

export function getSponsor(id: number): Sponsor | null {
  return ((getDb().prepare("SELECT * FROM sponsors WHERE id = ?").get(id) as Sponsor) ?? null);
}

export function updateSponsor(
  id: number,
  name: string,
  company: string,
  whatsapp: string,
  email: string,
  notes: string
): void {
  getDb()
    .prepare("UPDATE sponsors SET name=?, company=?, whatsapp=?, email=?, notes=? WHERE id=?")
    .run(name, company, whatsapp, email, notes, id);
}

export function deleteSponsor(id: number): void {
  const db = getDb();
  const tx = db.transaction(() => {
    db.prepare("UPDATE students SET sponsor_id = NULL WHERE sponsor_id = ?").run(id);
    db.prepare("UPDATE scheduled_messages SET recipient_id = NULL WHERE recipient_id = ?").run(id);
    db.prepare("DELETE FROM sponsors WHERE id = ?").run(id);
  });
  tx();
}

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
  if (limit !== undefined) {
    return getDb()
      .prepare("SELECT * FROM message_history ORDER BY id DESC LIMIT ?")
      .all(limit) as MessageRecord[];
  }
  return getDb()
    .prepare("SELECT * FROM message_history ORDER BY id DESC")
    .all() as MessageRecord[];
}

export function getMessagesByDay(days = 30): { date: string; count: number }[] {
  const safeDays = Math.min(Math.max(Math.floor(days), 1), 365);
  return getDb()
    .prepare(
      `SELECT date, COUNT(*) as count
       FROM message_history
       WHERE date >= date('now', ? || ' days')
       GROUP BY date
       ORDER BY date ASC`
    )
    .all(`-${safeDays}`) as { date: string; count: number }[];
}

export function addScheduledMessage(
  recipientId: number | null,
  recipientName: string,
  channel: string,
  subject: string,
  message: string,
  sendTime: string
): number {
  const result = getDb()
    .prepare(
      "INSERT INTO scheduled_messages (recipient, recipient_id, channel, subject, message, send_time, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')"
    )
    .run(recipientName, recipientId, channel, subject, message, sendTime);
  return result.lastInsertRowid as number;
}

export function getScheduledMessages(status?: string | null): ScheduledMessage[] {
  const baseQuery = `SELECT sm.*, COALESCE(sp.name, sm.recipient) as recipient_name
    FROM scheduled_messages sm
    LEFT JOIN sponsors sp ON sm.recipient_id = sp.id`;

  if (status) {
    return getDb()
      .prepare(`${baseQuery} WHERE sm.status = ? ORDER BY sm.send_time ASC`)
      .all(status) as ScheduledMessage[];
  }

  return getDb()
    .prepare(`${baseQuery} ORDER BY sm.send_time ASC`)
    .all() as ScheduledMessage[];
}

export function getScheduledMessage(id: number): ScheduledMessage | null {
  return (
    (getDb()
      .prepare(
        `SELECT sm.*, COALESCE(sp.name, sm.recipient) as recipient_name
         FROM scheduled_messages sm
         LEFT JOIN sponsors sp ON sm.recipient_id = sp.id
         WHERE sm.id = ?`
      )
      .get(id) as ScheduledMessage) ?? null
  );
}

export function getDueScheduledMessages(): ScheduledMessage[] {
  const now = new Date().toISOString();
  return getDb()
    .prepare(
      `SELECT sm.*, COALESCE(sp.name, sm.recipient) as recipient_name
       FROM scheduled_messages sm
       LEFT JOIN sponsors sp ON sm.recipient_id = sp.id
       WHERE sm.status = 'pending' AND sm.send_time <= ?
       ORDER BY sm.send_time ASC`
    )
    .all(now) as ScheduledMessage[];
}

export function updateScheduledMessageStatus(id: number, status: string): void {
  getDb().prepare("UPDATE scheduled_messages SET status = ? WHERE id = ?").run(status, id);
}

export function getGrades(): Grade[] {
  return getDb().prepare("SELECT * FROM grades ORDER BY id").all() as Grade[];
}

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

const studentSelect = `SELECT s.id, s.student_code, s.name, s.age, s.contact_info, s.address,
        s.grade_id, s.sponsor_id, s.auto_send, s.notes,
        g.name  as grade_name,
        sp.name as sponsor_name,
        sp.email as sponsor_email,
        sp.whatsapp as sponsor_phone
 FROM students s
 LEFT JOIN grades g ON s.grade_id = g.id
 LEFT JOIN sponsors sp ON s.sponsor_id = sp.id`;

export function getStudents(): Student[] {
  return getDb().prepare(`${studentSelect} ORDER BY s.name`).all() as Student[];
}

export function getStudent(id: number): Student | null {
  return (
    (getDb().prepare(`${studentSelect} WHERE s.id = ?`).get(id) as Student) ?? null
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
  getDb().prepare("UPDATE students SET auto_send = ? WHERE id = ?").run(autoSend ? 1 : 0, id);
}

export function getStudentsByNameFragment(fragment: string): Student[] {
  return getDb()
    .prepare("SELECT id, name, student_code FROM students WHERE name LIKE ? ORDER BY name")
    .all(`%${fragment}%`) as Student[];
}

export function addReport(studentId: number, filePath: string, fileName: string): number {
  const result = getDb()
    .prepare(
      `INSERT INTO reports (student_id, file_path, file_name, upload_date, message_sent, sent_to)
       VALUES (?, ?, ?, datetime('now'), 0, NULL)`
    )
    .run(studentId, filePath, fileName);
  return result.lastInsertRowid as number;
}

export function getReports(studentId?: number): Report[] {
  const baseQuery = `SELECT r.*, s.name as student_name
    FROM reports r
    JOIN students s ON r.student_id = s.id`;
  if (studentId) {
    return getDb()
      .prepare(`${baseQuery} WHERE r.student_id = ? ORDER BY r.upload_date DESC`)
      .all(studentId) as Report[];
  }
  return getDb()
    .prepare(`${baseQuery} ORDER BY r.upload_date DESC`)
    .all() as Report[];
}

export function updateReportSent(reportId: number, sentTo: string): void {
  getDb()
    .prepare("UPDATE reports SET message_sent = 1, sent_to = ? WHERE id = ?")
    .run(sentTo, reportId);
}

export function deleteReport(id: number): void {
  getDb().prepare("DELETE FROM reports WHERE id = ?").run(id);
}

export function addPaymentCommitment(
  sponsorId: number,
  studentId: number | null,
  amountCommitted: number,
  amountReceived: number,
  currency: string,
  frequency: string,
  commitmentDate: string,
  nextDueDate: string | null,
  lastPaymentDate: string | null,
  status: string,
  notes: string
): number {
  const result = getDb()
    .prepare(
      `INSERT INTO payment_commitments
        (sponsor_id, student_id, amount_committed, amount_received, currency, frequency, commitment_date, next_due_date, last_payment_date, status, notes)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      sponsorId,
      studentId,
      amountCommitted,
      amountReceived,
      currency,
      frequency,
      commitmentDate,
      nextDueDate,
      lastPaymentDate,
      status,
      notes
    );
  return result.lastInsertRowid as number;
}

export function getPaymentCommitments(): PaymentCommitment[] {
  return getDb()
    .prepare(
      `SELECT pc.*, sp.name as sponsor_name, st.name as student_name
       FROM payment_commitments pc
       JOIN sponsors sp ON pc.sponsor_id = sp.id
       LEFT JOIN students st ON pc.student_id = st.id
       ORDER BY COALESCE(pc.next_due_date, pc.commitment_date) ASC, pc.id DESC`
    )
    .all() as PaymentCommitment[];
}

export function getPaymentCommitment(id: number): PaymentCommitment | null {
  return (
    (getDb()
      .prepare(
        `SELECT pc.*, sp.name as sponsor_name, st.name as student_name
         FROM payment_commitments pc
         JOIN sponsors sp ON pc.sponsor_id = sp.id
         LEFT JOIN students st ON pc.student_id = st.id
         WHERE pc.id = ?`
      )
      .get(id) as PaymentCommitment) ?? null
  );
}

export function updatePaymentCommitment(
  id: number,
  sponsorId: number,
  studentId: number | null,
  amountCommitted: number,
  amountReceived: number,
  currency: string,
  frequency: string,
  commitmentDate: string,
  nextDueDate: string | null,
  lastPaymentDate: string | null,
  status: string,
  notes: string
): void {
  getDb()
    .prepare(
      `UPDATE payment_commitments
       SET sponsor_id=?, student_id=?, amount_committed=?, amount_received=?, currency=?, frequency=?, commitment_date=?, next_due_date=?, last_payment_date=?, status=?, notes=?
       WHERE id=?`
    )
    .run(
      sponsorId,
      studentId,
      amountCommitted,
      amountReceived,
      currency,
      frequency,
      commitmentDate,
      nextDueDate,
      lastPaymentDate,
      status,
      notes,
      id
    );
}

export function deletePaymentCommitment(id: number): void {
  getDb().prepare("DELETE FROM payment_commitments WHERE id = ?").run(id);
}

export function addCalendarEvent(
  title: string,
  description: string,
  startTime: string,
  endTime: string | null,
  location: string,
  sponsorId: number | null,
  studentId: number | null,
  source: string
): number {
  const result = getDb()
    .prepare(
      `INSERT INTO calendar_events
        (title, description, start_time, end_time, location, sponsor_id, student_id, source)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(title, description, startTime, endTime, location, sponsorId, studentId, source);
  return result.lastInsertRowid as number;
}

export function getCalendarEvents(): CalendarEvent[] {
  return getDb()
    .prepare(
      `SELECT ce.*, sp.name as sponsor_name, st.name as student_name
       FROM calendar_events ce
       LEFT JOIN sponsors sp ON ce.sponsor_id = sp.id
       LEFT JOIN students st ON ce.student_id = st.id
       ORDER BY ce.start_time ASC, ce.id ASC`
    )
    .all() as CalendarEvent[];
}

export function getCalendarEvent(id: number): CalendarEvent | null {
  return (
    (getDb()
      .prepare(
        `SELECT ce.*, sp.name as sponsor_name, st.name as student_name
         FROM calendar_events ce
         LEFT JOIN sponsors sp ON ce.sponsor_id = sp.id
         LEFT JOIN students st ON ce.student_id = st.id
         WHERE ce.id = ?`
      )
      .get(id) as CalendarEvent) ?? null
  );
}

export function updateCalendarEvent(
  id: number,
  title: string,
  description: string,
  startTime: string,
  endTime: string | null,
  location: string,
  sponsorId: number | null,
  studentId: number | null,
  source: string
): void {
  getDb()
    .prepare(
      `UPDATE calendar_events
       SET title=?, description=?, start_time=?, end_time=?, location=?, sponsor_id=?, student_id=?, source=?
       WHERE id=?`
    )
    .run(title, description, startTime, endTime, location, sponsorId, studentId, source, id);
}

export function deleteCalendarEvent(id: number): void {
  getDb().prepare("DELETE FROM calendar_events WHERE id = ?").run(id);
}

export function getDashboardStats() {
  const db = getDb();
  const totalSponsors = (db.prepare("SELECT COUNT(*) as c FROM sponsors").get() as { c: number }).c;
  const totalStudents = (db.prepare("SELECT COUNT(*) as c FROM students").get() as { c: number }).c;
  const totalMessages = (db.prepare("SELECT COUNT(*) as c FROM message_history").get() as { c: number }).c;
  const pendingScheduled = (
    db.prepare("SELECT COUNT(*) as c FROM scheduled_messages WHERE status = 'pending'").get() as { c: number }
  ).c;

  const recentMessages = db
    .prepare("SELECT * FROM message_history ORDER BY id DESC LIMIT 10")
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
