import { NextRequest, NextResponse } from "next/server";
import { get, query, run } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const status = searchParams.get("status") ?? "pending";
  try {
    const messages = query(
      `SELECT sm.*, COALESCE(sp.name, sm.recipient) AS recipient_name
       FROM scheduled_messages sm
       LEFT JOIN sponsors sp ON sm.recipient_id = sp.id
       WHERE sm.status = ?
       ORDER BY sm.send_time ASC`,
      [status]
    );
    return NextResponse.json({ success: true, data: messages });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const { recipient, recipient_id, channel, subject = "", message, send_time } = await req.json();
    if (!channel || !message || !send_time) {
      return NextResponse.json(
        { success: false, error: "channel, message and send_time are required" },
        { status: 400 }
      );
    }

    const parsedTime = new Date(send_time);
    if (Number.isNaN(parsedTime.getTime())) {
      return NextResponse.json({ success: false, error: "Invalid send_time" }, { status: 400 });
    }
    if (parsedTime.getTime() <= Date.now()) {
      return NextResponse.json(
        { success: false, error: "send_time must be in the future" },
        { status: 400 }
      );
    }

    let resolvedId: number | null = null;
    let resolvedName: string = String(recipient ?? "");

    if (recipient_id) {
      const sponsor = get<{ id: number; name: string }>("SELECT id, name FROM sponsors WHERE id = ?", [Number(recipient_id)]);
      if (!sponsor) {
        return NextResponse.json({ success: false, error: "Sponsor not found" }, { status: 404 });
      }
      resolvedId = sponsor.id;
      resolvedName = sponsor.name;
    }

    const result = run(
      `INSERT INTO scheduled_messages (recipient, recipient_id, channel, subject, message, send_time, status)
       VALUES (?, ?, ?, ?, ?, ?, 'pending')`,
      [resolvedName, resolvedId, channel, String(subject).trim(), String(message).trim(), parsedTime.toISOString()]
    );
    const id = result.lastInsertRowid;

    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
