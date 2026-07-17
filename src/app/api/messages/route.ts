import { NextRequest, NextResponse } from "next/server";
import { query } from "@/lib/db-utils";
import { POST as sendMessage } from "./send/route";

export const runtime = "nodejs";

export async function GET() {
  try {
    const messages = query(
      "SELECT id, date, recipient, channel, direction, message, status FROM message_history ORDER BY id DESC"
    );
    return NextResponse.json({ success: true, data: messages });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  return sendMessage(req);
}
