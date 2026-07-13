import { NextRequest, NextResponse } from "next/server";
import { addScheduledMessage, getScheduledMessages, getSponsor } from "@/lib/db";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const status = searchParams.get("status");
  try {
    const messages = getScheduledMessages(status ?? undefined);
    return NextResponse.json({ success: true, data: messages });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const { recipient_id, channel, subject = "", message, send_time } = await req.json();
    if (!recipient_id || !channel || !message || !send_time) {
      return NextResponse.json({ success: false, error: "recipient_id, channel, message and send_time are required" }, { status: 400 });
    }

    const sponsor = getSponsor(Number(recipient_id));
    if (!sponsor) {
      return NextResponse.json({ success: false, error: "Sponsor not found" }, { status: 404 });
    }

    const parsedTime = new Date(send_time);
    if (Number.isNaN(parsedTime.getTime())) {
      return NextResponse.json({ success: false, error: "Invalid send_time" }, { status: 400 });
    }
    if (parsedTime.getTime() <= Date.now()) {
      return NextResponse.json({ success: false, error: "send_time must be in the future" }, { status: 400 });
    }

    const id = addScheduledMessage(
      sponsor.id,
      sponsor.name,
      channel,
      String(subject ?? "").trim(),
      String(message).trim(),
      parsedTime.toISOString()
    );
    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
