import { NextRequest, NextResponse } from "next/server";
import { get, run } from "@/lib/db-utils";
import fs from "fs";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const reportId = Number(id);
  if (!Number.isInteger(reportId) || reportId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid report id" }, { status: 400 });
  }

  try {
    const report = get<{ file_path: string | null }>("SELECT file_path FROM reports WHERE id = ?", [reportId]);
    if (report?.file_path && fs.existsSync(report.file_path)) {
      try { fs.unlinkSync(report.file_path); } catch { /* ignore */ }
    }
    const result = run("DELETE FROM reports WHERE id = ?", [reportId]);
    if (!result.changes) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PATCH(req: NextRequest, { params }: Params) {
  const { id } = await params;
  const reportId = Number(id);
  if (!Number.isInteger(reportId) || reportId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid report id" }, { status: 400 });
  }

  try {
    const { sent_to } = await req.json();
    if (!sent_to) {
      return NextResponse.json({ success: false, error: "sent_to is required" }, { status: 400 });
    }
    const result = run("UPDATE reports SET message_sent = 1, sent_to = ? WHERE id = ?", [String(sent_to), reportId]);
    if (!result.changes) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
