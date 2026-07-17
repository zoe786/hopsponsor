import { NextRequest, NextResponse } from "next/server";
import { getScheduledMessage, updateScheduledMessageStatus } from "@/lib/db";

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

    if (scheduled.status === "sent") {
      return NextResponse.json({ success: false, error: "Sent messages cannot be cancelled" }, { status: 400 });
    }

    updateScheduledMessageStatus(messageId, "cancelled");
    return NextResponse.json({ success: true, data: { id: messageId, status: "cancelled" } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
