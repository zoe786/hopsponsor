import { NextRequest, NextResponse } from "next/server";
import { getGrades } from "@/lib/db";

export const runtime = "nodejs";

export async function GET(_req: NextRequest) {
  try {
    const grades = getGrades();
    return NextResponse.json({ success: true, data: grades });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
