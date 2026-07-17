import { NextRequest, NextResponse } from "next/server";
import { query, run } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function GET() {
  try {
    const styles = query(
      "SELECT id, category, message, golden_example FROM style_library ORDER BY id DESC"
    );
    return NextResponse.json({ success: true, data: styles });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const { category, message, golden_example = false } = await req.json();
    if (!category?.trim() || !message?.trim()) {
      return NextResponse.json({ success: false, error: "Category and message are required" }, { status: 400 });
    }
    const result = run(
      "INSERT INTO style_library (category, message, golden_example) VALUES (?, ?, ?)",
      [category.trim(), message.trim(), Boolean(golden_example) ? 1 : 0]
    );
    const id = result.lastInsertRowid;
    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
