import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { randomUUID } from "crypto";
import { get, run, todayDateString } from "@/lib/db-utils";
import { sendEmailWithAttachment } from "@/lib/ai";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const files = formData.getAll("files") as File[];
    const studentId = Number(formData.get("student_id"));

    if (!files.length) {
      return NextResponse.json({ success: false, error: "No files provided" }, { status: 400 });
    }
    if (!Number.isInteger(studentId) || studentId <= 0) {
      return NextResponse.json({ success: false, error: "student_id is required" }, { status: 400 });
    }

    const student = get<{
      id: number;
      name: string;
      auto_send: number;
      sponsor_name: string | null;
      sponsor_email: string | null;
    }>(
      `SELECT s.id, s.name, s.auto_send, sp.name AS sponsor_name, sp.email AS sponsor_email
       FROM students s
       LEFT JOIN sponsors sp ON s.sponsor_id = sp.id
       WHERE s.id = ?`,
      [studentId]
    );
    if (!student) {
      return NextResponse.json({ success: false, error: "Student not found" }, { status: 404 });
    }

    const uploadsDir = path.join(process.cwd(), "uploads", "reports");
    fs.mkdirSync(uploadsDir, { recursive: true });

    const results: Array<{ id: number; file_name: string; sent: boolean; sent_to: string | null }> = [];

    for (const file of files) {
      const originalName = path.basename(file.name);
      const safeName = originalName.replace(/[^a-zA-Z0-9._-]/g, "_");
      const storedName = `${Date.now()}_${randomUUID()}_${safeName}`;
      const absolutePath = path.join(uploadsDir, storedName);
      const relativePath = path.join("uploads", "reports", storedName);
      const data = Buffer.from(await file.arrayBuffer());
      fs.writeFileSync(absolutePath, data);

      const uploadDate = todayDateString();
      const insert = run(
        "INSERT INTO reports (student_id, file_path, file_name, upload_date, message_sent, sent_to) VALUES (?, ?, ?, ?, 0, NULL)",
        [student.id, relativePath, file.name, uploadDate]
      );
      const reportId = insert.lastInsertRowid;

      let sent = false;
      let sentTo: string | null = null;
      if (student.auto_send && student.sponsor_email) {
        const body = `Dear ${student.sponsor_name ?? "Sponsor"},<br/><br/>Please find attached the latest report for ${student.name}.`;
        const emailResult = await sendEmailWithAttachment(
          student.sponsor_email,
          `Student Report - ${student.name}`,
          body,
          data,
          safeName
        );

        if (emailResult.success) {
          sent = true;
          sentTo = student.sponsor_email;
          run("UPDATE reports SET message_sent = 1, sent_to = ? WHERE id = ?", [sentTo, reportId]);
          run(
            "INSERT INTO message_history (date, recipient, channel, direction, message, status) VALUES (?, ?, ?, ?, ?, ?)",
            [
              todayDateString(),
              student.sponsor_name ?? "Sponsor",
              "Email",
              "Outbound",
              `Report sent for ${student.name}: ${file.name}`,
              "Sent",
            ]
          );
        }
      }

      results.push({ id: reportId, file_name: file.name, sent, sent_to: sentTo });
    }

    return NextResponse.json({ success: true, data: results }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
