import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db-utils";
import { POST as uploadReport } from "./upload/route";

export const runtime = "nodejs";

export async function GET() {
  try {
    const reports = query(
      `SELECT r.id, r.student_id, s.name AS student_name, r.file_path, r.file_name,
              r.upload_date, r.message_sent, r.sent_to
       FROM reports r
       JOIN students s ON r.student_id = s.id
       ORDER BY r.upload_date DESC`
    );
    return NextResponse.json({ success: true, data: reports });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  return uploadReport(req);
}
