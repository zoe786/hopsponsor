import { NextRequest, NextResponse } from "next/server";
import { addMessage, getSponsor } from "@/lib/db";
import { sendEmail, sendWhatsApp } from "@/lib/ai";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const { recipient, channel, subject = "", message } = await req.json();
    if (!recipient || !channel || !message) {
      return NextResponse.json(
        { success: false, error: "recipient, channel and message are required" },
        { status: 400 }
      );
    }

    const sponsor = getSponsor(Number(recipient));
    if (!sponsor) {
      return NextResponse.json({ success: false, error: "Sponsor not found" }, { status: 404 });
    }

    let result: { success: boolean; error?: string };
    if (channel === "Email") {
      if (!sponsor.email) {
        return NextResponse.json(
          { success: false, error: "Sponsor has no email address" },
          { status: 400 }
        );
      }
      result = await sendEmail(sponsor.email, subject || "Message from HOPe", message);
    } else if (channel === "WhatsApp") {
      if (!sponsor.whatsapp) {
        return NextResponse.json(
          { success: false, error: "Sponsor has no WhatsApp number" },
          { status: 400 }
        );
      }
      result = await sendWhatsApp(sponsor.whatsapp, message);
    } else {
      return NextResponse.json({ success: false, error: "Unknown channel" }, { status: 400 });
    }

    if (result.success) {
      const today = new Date().toISOString().split("T")[0];
      addMessage(today, sponsor.name, channel, "Outbound", message, "Sent");
    }

    return NextResponse.json(result);
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
