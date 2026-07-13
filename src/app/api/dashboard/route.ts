import { NextResponse } from "next/server";
import { getDashboardStats } from "@/lib/db";

export const runtime = "nodejs";

export async function GET() {
  try {
    const data = getDashboardStats();
    return NextResponse.json({ success: true, data });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: String(err) },
      { status: 500 }
    );
  }
}
