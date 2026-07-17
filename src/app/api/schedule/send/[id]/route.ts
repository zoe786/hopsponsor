import { NextRequest, NextResponse } from "next/server";
import {
  addMessage,
  getScheduledMessage,
  getSponsor,
  updateScheduledMessageStatus,
} from "@/lib/db";
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
    const scheduled = getScheduledMessage(messageId);
    if (!scheduled) {
      return NextResponse.json({ success: false, error: "Scheduled message not found" }, { status: 404 });
    }

    if (scheduled.status !== "pending") {
      return NextResponse.json(
        { success: false, error: `Cannot send message with status '${scheduled.status}'` },
        { status: 400 }
      );
    }

    const sponsor = scheduled.recipient_id ? getSponsor(scheduled.recipient_id) : null;
    if (!sponsor) {
      updateScheduledMessageStatus(scheduled.id, "failed");
      return NextResponse.json(
        { success: false, error: "Sponsor not found for scheduled message" },
        { status: 404 }
      );
    }

    let sendResult: { success: boolean; error?: string };
    if (scheduled.channel === "Email") {
      if (!sponsor.email) {
        updateScheduledMessageStatus(scheduled.id, "failed");
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
        updateScheduledMessageStatus(scheduled.id, "failed");
        return NextResponse.json(
          { success: false, error: "Sponsor has no WhatsApp number" },
          { status: 400 }
        );
      }
      sendResult = await sendWhatsApp(sponsor.whatsapp, scheduled.message);
    } else {
      updateScheduledMessageStatus(scheduled.id, "failed");
      return NextResponse.json({ success: false, error: "Unknown channel" }, { status: 400 });
    }

    if (!sendResult.success) {
      updateScheduledMessageStatus(scheduled.id, "failed");
      return NextResponse.json(
        { success: false, error: sendResult.error ?? "Failed to send scheduled message" },
        { status: 502 }
      );
    }

    addMessage(
      new Date().toISOString().split("T")[0],
      sponsor.name,
      scheduled.channel,
      "Outbound",
      scheduled.message,
      "Sent"
    );
    updateScheduledMessageStatus(scheduled.id, "sent");

    return NextResponse.json({ success: true, data: { id: scheduled.id, status: "sent" } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
