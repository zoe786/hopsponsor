import { NextResponse } from "next/server";
import { addMessage, getDueScheduledMessages, getSponsor, updateScheduledMessageStatus } from "@/lib/db";
import { sendEmail, sendWhatsApp } from "@/lib/ai";

export const runtime = "nodejs";

export async function POST() {
  try {
    const dueMessages = getDueScheduledMessages();
    const results: { id: number; status: string; error?: string }[] = [];

    for (const msg of dueMessages) {
      const sponsor = msg.recipient_id ? getSponsor(msg.recipient_id) : null;
      if (!sponsor) {
        results.push({ id: msg.id, status: "skipped", error: "Sponsor not found" });
        updateScheduledMessageStatus(msg.id, "failed");
        continue;
      }

      let sendResult: { success: boolean; error?: string };

      if (msg.channel === "Email") {
        if (!sponsor.email) {
          results.push({ id: msg.id, status: "skipped", error: "No email" });
          updateScheduledMessageStatus(msg.id, "failed");
          continue;
        }
        sendResult = await sendEmail(
          sponsor.email,
          msg.subject || `Scheduled message for ${sponsor.name}`,
          msg.message
        );
      } else if (msg.channel === "WhatsApp") {
        if (!sponsor.whatsapp) {
          results.push({ id: msg.id, status: "skipped", error: "No WhatsApp" });
          updateScheduledMessageStatus(msg.id, "failed");
          continue;
        }
        sendResult = await sendWhatsApp(sponsor.whatsapp, msg.message);
      } else {
        results.push({ id: msg.id, status: "skipped", error: "Unknown channel" });
        updateScheduledMessageStatus(msg.id, "failed");
        continue;
      }

      if (sendResult.success) {
        const today = new Date().toISOString().split("T")[0];
        addMessage(today, sponsor.name, msg.channel, "Outbound", msg.message, "Sent");
        updateScheduledMessageStatus(msg.id, "sent");
        results.push({ id: msg.id, status: "sent" });
      } else {
        updateScheduledMessageStatus(msg.id, "failed");
        results.push({ id: msg.id, status: "failed", error: sendResult.error });
      }
    }

    return NextResponse.json({ success: true, data: { processed: results.length, results } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
