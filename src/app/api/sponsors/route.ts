import { NextRequest, NextResponse } from "next/server";
import { query, run } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function GET() {
  try {
    const sponsors = query(
      "SELECT id, name, company, whatsapp, email, notes FROM sponsors ORDER BY name"
    );
    return NextResponse.json({ success: true, data: sponsors });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, company = "", whatsapp = "", email = "", notes = "" } = body;
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }
    const result = run(
      "INSERT INTO sponsors (name, company, whatsapp, email, notes) VALUES (?, ?, ?, ?, ?)",
      [name.trim(), company, whatsapp, email, notes]
    );
    const id = result.lastInsertRowid;
    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
