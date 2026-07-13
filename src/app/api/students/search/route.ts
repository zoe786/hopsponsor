import { NextRequest, NextResponse } from "next/server";
import { getStudentsByNameFragment } from "@/lib/db";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const q = (searchParams.get("q") || "").trim();
    if (!q) return NextResponse.json({ success: true, data: [] });
    return NextResponse.json({ success: true, data: getStudentsByNameFragment(q) });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
