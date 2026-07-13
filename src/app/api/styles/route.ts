import { NextRequest, NextResponse } from "next/server";
import { getStyles, addStyle } from "@/lib/db";

export const runtime = "nodejs";

export async function GET() {
  try {
    const styles = getStyles();
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
    const id = addStyle(category.trim(), message.trim(), Boolean(golden_example));
    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
