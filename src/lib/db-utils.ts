import type Database from "better-sqlite3";
import { getDb } from "./db";

type SqlParam = string | number | null;

let seedChecked = false;
let seedInProgress = false;

function rawQuery<T>(sql: string, params: SqlParam[] = []): T[] {
  const db = getDb();
  return db.prepare(sql).all(...params) as T[];
}

function rawGet<T>(sql: string, params: SqlParam[] = []): T | null {
  const db = getDb();
  return (db.prepare(sql).get(...params) as T) ?? null;
}

function rawRun(sql: string, params: SqlParam[] = []) {
  const db = getDb();
  const result = db.prepare(sql).run(...params);
  return {
    changes: result.changes,
    lastInsertRowid: Number(result.lastInsertRowid),
  };
}

function nextStudentCode(): string {
  const row = rawGet<{ max_code: number | null }>(
    "SELECT MAX(CAST(SUBSTR(student_code, 5) AS INTEGER)) as max_code FROM students WHERE student_code LIKE 'STU-%'"
  );
  return `STU-${String((row?.max_code ?? 0) + 1).padStart(4, "0")}`;
}

export function generateNextStudentCode(): string {
  ensureSeedData();
  return nextStudentCode();
}

export function todayDateString(): string {
  return new Date().toISOString().split("T")[0];
}

function ensureSeedData() {
  if (seedChecked || seedInProgress) return;
  seedInProgress = true;

  try {
    const sponsorCount = rawGet<{ count: number }>("SELECT COUNT(*) as count FROM sponsors")?.count ?? 0;
    if (sponsorCount === 0) {
      rawRun(
        "INSERT INTO sponsors (name, company, whatsapp, email, notes) VALUES (?, ?, ?, ?, ?)",
        ["John Kamau", "Kamau Holdings", "+254700111222", "john@kamauholdings.com", "Supports STEM scholarships"]
      );
      rawRun(
        "INSERT INTO sponsors (name, company, whatsapp, email, notes) VALUES (?, ?, ?, ?, ?)",
        ["Amina Hassan", "AHS Foundation", "+254700333444", "amina@ahs.foundation", "Interested in girls education"]
      );
      rawRun(
        "INSERT INTO sponsors (name, company, whatsapp, email, notes) VALUES (?, ?, ?, ?, ?)",
        ["David Otieno", "Otieno Group", "+254700555666", "david@otienogroup.org", "Wants quarterly progress updates"]
      );
    }

    const studentCount = rawGet<{ count: number }>("SELECT COUNT(*) as count FROM students")?.count ?? 0;
    if (studentCount === 0) {
      const grade5Id = rawGet<{ id: number }>("SELECT id FROM grades WHERE name = ?", ["Grade 5"])?.id ?? null;
      const form2Id = rawGet<{ id: number }>("SELECT id FROM grades WHERE name = ?", ["Form 2"])?.id ?? null;
      const grade3Id = rawGet<{ id: number }>("SELECT id FROM grades WHERE name = ?", ["Grade 3"])?.id ?? null;

      const sponsors = rawQuery<{ id: number }>("SELECT id FROM sponsors ORDER BY id LIMIT 3");

      rawRun(
        `INSERT INTO students (student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          nextStudentCode(),
          "Grace Wanjiku",
          11,
          "Guardian: +254711111111",
          "Nairobi",
          grade5Id,
          sponsors[0]?.id ?? null,
          1,
          "Excellent in mathematics",
        ]
      );
      rawRun(
        `INSERT INTO students (student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          nextStudentCode(),
          "Brian Kiptoo",
          15,
          "Guardian: +254722222222",
          "Nakuru",
          form2Id,
          sponsors[1]?.id ?? null,
          1,
          "Needs support in science projects",
        ]
      );
      rawRun(
        `INSERT INTO students (student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          nextStudentCode(),
          "Sarah Achieng",
          9,
          "Guardian: +254733333333",
          "Kisumu",
          grade3Id,
          sponsors[2]?.id ?? null,
          1,
          "Consistent attendance and progress",
        ]
      );
    }

    const styleCount = rawGet<{ count: number }>("SELECT COUNT(*) as count FROM style_library")?.count ?? 0;
    if (styleCount === 0) {
      rawRun(
        "INSERT INTO style_library (category, message, golden_example) VALUES (?, ?, ?)",
        [
          "Thank You",
          "Dear {sponsor_name}, thank you for your generous support. Your kindness continues to transform our students' lives.",
          1,
        ]
      );
    }

    const messageCount = rawGet<{ count: number }>("SELECT COUNT(*) as count FROM message_history")?.count ?? 0;
    if (messageCount === 0) {
      rawRun(
        "INSERT INTO message_history (date, recipient, channel, direction, message, status) VALUES (?, ?, ?, ?, ?, ?)",
        [
          todayDateString(),
          "John Kamau",
          "Email",
          "Outbound",
          "Welcome to HOPe Management. Thank you for supporting our students.",
          "Sent",
        ]
      );
    }
    seedChecked = true;
  } catch (err) {
    seedChecked = false;
    throw err;
  } finally {
    seedInProgress = false;
  }
}

export function query<T>(sql: string, params: SqlParam[] = []): T[] {
  ensureSeedData();
  return rawQuery<T>(sql, params);
}

export function get<T>(sql: string, params: SqlParam[] = []): T | null {
  ensureSeedData();
  return rawGet<T>(sql, params);
}

export function run(sql: string, params: SqlParam[] = []) {
  ensureSeedData();
  return rawRun(sql, params);
}

export function transaction<T>(fn: (db: Database.Database) => T): T {
  ensureSeedData();
  const db = getDb();
  return db.transaction(() => fn(db))();
}
