import { NextResponse } from "next/server";
import { getDueScheduledMessages, updateScheduledMessageStatus, addMessage } from "@/lib/db";
import { sendEmail, sendWhatsApp } from "@/lib/ai";
import { getSponsors } from "@/lib/db";

export const runtime = "nodejs";

export async function POST() {
  try {
    const dueMessages = getDueScheduledMessages();
    const sponsors = getSponsors();
    const results: { id: number; status: string; error?: string }[] = [];

    for (const msg of dueMessages) {
      const sponsor = sponsors.find((s) => s.name === msg.recipient);
      if (!sponsor) {
        results.push({ id: msg.id, status: "skipped", error: "Sponsor not found" });
        continue;
      }

      let sendResult: { success: boolean; error?: string };

      if (msg.channel === "Email") {
        if (!sponsor.email) {
          results.push({ id: msg.id, status: "skipped", error: "No email" });
          continue;
        }
        sendResult = await sendEmail(sponsor.email, `Scheduled message for ${msg.recipient}`, msg.message);
      } else if (msg.channel === "WhatsApp") {
        if (!sponsor.whatsapp) {
          results.push({ id: msg.id, status: "skipped", error: "No WhatsApp" });
          continue;
        }
        sendResult = await sendWhatsApp(sponsor.whatsapp, msg.message);
      } else {
        results.push({ id: msg.id, status: "skipped", error: "Unknown channel" });
        continue;
      }

      if (sendResult.success) {
        const today = new Date().toISOString().split("T")[0];
        addMessage(today, msg.recipient, msg.channel, "Outbound", msg.message, "Sent");
        updateScheduledMessageStatus(msg.id, "sent");
        results.push({ id: msg.id, status: "sent" });
      } else {
        results.push({ id: msg.id, status: "failed", error: sendResult.error });
      }
    }

    return NextResponse.json({ success: true, data: { processed: results.length, results } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
