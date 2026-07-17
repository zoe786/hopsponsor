import { NextRequest, NextResponse } from "next/server";
import { deleteReport, getReports, updateReportSent } from "@/lib/db";
import fs from "fs";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const reports = getReports();
    const report = reports.find((r) => r.id === Number(id));
    if (report?.file_path && fs.existsSync(report.file_path)) {
      try { fs.unlinkSync(report.file_path); } catch { /* ignore */ }
    }
    deleteReport(Number(id));
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PATCH(req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const { sent_to } = await req.json();
    if (!sent_to) {
      return NextResponse.json({ success: false, error: "sent_to is required" }, { status: 400 });
    }
    updateReportSent(Number(id), String(sent_to));
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
