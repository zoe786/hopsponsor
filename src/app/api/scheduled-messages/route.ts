import { NextRequest, NextResponse } from "next/server";
import { getScheduledMessages, addScheduledMessage } from "@/lib/db";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const status = searchParams.get("status"); // "pending" | "sent" | "cancelled" | null for all
  try {
    const messages = getScheduledMessages(status ?? undefined);
    return NextResponse.json({ success: true, data: messages });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const { recipient, channel, message, send_time } = await req.json();
    if (!recipient || !channel || !message || !send_time) {
      return NextResponse.json({ success: false, error: "All fields required" }, { status: 400 });
    }
    const id = addScheduledMessage(recipient, channel, message, send_time);
    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
