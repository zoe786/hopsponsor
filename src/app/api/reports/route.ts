import { NextRequest, NextResponse } from "next/server";
import { addReport, getReports, getStudents } from "@/lib/db";
import { matchFilesToStudents } from "@/lib/ai";
import fs from "fs";
import path from "path";

export const runtime = "nodejs";

const REPORTS_DIR = process.env.REPORTS_DIR || "./data/reports";

function ensureReportsDir() {
  if (!fs.existsSync(REPORTS_DIR)) fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

export async function GET() {
  try {
    return NextResponse.json({ success: true, data: getReports() });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const files = formData.getAll("files") as File[];
    const autoMatch = formData.get("auto_match") === "true";

    if (!files.length) {
      return NextResponse.json({ success: false, error: "No files provided" }, { status: 400 });
    }

    ensureReportsDir();

    const students = getStudents();
    const studentNames = students.map((s) => s.name);

    let matches: { fileName: string; studentName: string | null }[] = [];
    if (autoMatch && students.length > 0) {
      const fileNames = files.map((f) => path.parse(f.name).name);
      matches = await matchFilesToStudents(fileNames, studentNames);
    }

    const saved: { fileName: string; studentName: string | null; reportId: number | null }[] = [];

    for (const file of files) {
      const buffer = Buffer.from(await file.arrayBuffer());
      const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
      const timestamp = Date.now();
      const storedName = `${timestamp}_${safeName}`;
      const filePath = path.join(REPORTS_DIR, storedName);
      fs.writeFileSync(filePath, buffer);

      const baseName = path.parse(file.name).name;
      const match = matches.find((m) => m.fileName === baseName);
      const matchedStudentName = match?.studentName ?? null;
      const student = matchedStudentName
        ? students.find((s) => s.name === matchedStudentName) ?? null
        : null;

      let reportId: number | null = null;
      if (student) {
        reportId = addReport(student.id, filePath, file.name);
      }

      saved.push({ fileName: file.name, studentName: matchedStudentName, reportId });
    }

    return NextResponse.json({ success: true, data: saved }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
