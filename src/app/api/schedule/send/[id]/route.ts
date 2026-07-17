import { NextRequest, NextResponse } from "next/server";
import { get, run } from "@/lib/db-utils";
import { sendEmail, sendWhatsApp } from "@/lib/ai";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function POST(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const messageId = Number(id);

  if (!Number.isInteger(messageId) || messageId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid message id" }, { status: 400 });
  }

  try {
    const scheduled = get<{
      id: number;
      recipient_id: number | null;
      channel: string;
      subject: string;
      message: string;
      status: string;
    }>("SELECT id, recipient_id, channel, subject, message, status FROM scheduled_messages WHERE id = ?", [messageId]);
    if (!scheduled) {
      return NextResponse.json({ success: false, error: "Scheduled message not found" }, { status: 404 });
    }

    if (scheduled.status !== "pending") {
      return NextResponse.json(
        { success: false, error: `Cannot send message with status '${scheduled.status}'` },
        { status: 400 }
      );
    }

    const sponsor = scheduled.recipient_id
      ? get<{ id: number; name: string; email: string; whatsapp: string }>(
          "SELECT id, name, email, whatsapp FROM sponsors WHERE id = ?",
          [scheduled.recipient_id]
        )
      : null;
    if (!sponsor) {
      run("UPDATE scheduled_messages SET status = 'failed' WHERE id = ?", [scheduled.id]);
      return NextResponse.json(
        { success: false, error: "Sponsor not found for scheduled message" },
        { status: 404 }
      );
    }

    let sendResult: { success: boolean; error?: string };
    if (scheduled.channel === "Email") {
      if (!sponsor.email) {
        run("UPDATE scheduled_messages SET status = 'failed' WHERE id = ?", [scheduled.id]);
        return NextResponse.json(
          { success: false, error: "Sponsor has no email address" },
          { status: 400 }
        );
      }
      sendResult = await sendEmail(
        sponsor.email,
        scheduled.subject || `Scheduled message for ${sponsor.name}`,
        scheduled.message
      );
    } else if (scheduled.channel === "WhatsApp") {
      if (!sponsor.whatsapp) {
        run("UPDATE scheduled_messages SET status = 'failed' WHERE id = ?", [scheduled.id]);
        return NextResponse.json(
          { success: false, error: "Sponsor has no WhatsApp number" },
          { status: 400 }
        );
      }
      sendResult = await sendWhatsApp(sponsor.whatsapp, scheduled.message);
    } else {
      run("UPDATE scheduled_messages SET status = 'failed' WHERE id = ?", [scheduled.id]);
      return NextResponse.json({ success: false, error: "Unknown channel" }, { status: 400 });
    }

    if (!sendResult.success) {
      run("UPDATE scheduled_messages SET status = 'failed' WHERE id = ?", [scheduled.id]);
      return NextResponse.json(
        { success: false, error: sendResult.error ?? "Failed to send scheduled message" },
        { status: 502 }
      );
    }

    run(
      "INSERT INTO message_history (date, recipient, channel, direction, message, status) VALUES (?, ?, ?, ?, ?, ?)",
      [new Date().toISOString().split("T")[0], sponsor.name, scheduled.channel, "Outbound", scheduled.message, "Sent"]
    );
    run("UPDATE scheduled_messages SET status = 'sent' WHERE id = ?", [scheduled.id]);

    return NextResponse.json({ success: true, data: { id: scheduled.id, status: "sent" } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
