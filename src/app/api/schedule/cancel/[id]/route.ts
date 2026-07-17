import { NextRequest, NextResponse } from "next/server";
import { get, run } from "@/lib/db-utils";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function POST(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const messageId = Number(id);

  if (!Number.isInteger(messageId) || messageId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid message id" }, { status: 400 });
  }

  try {
    const scheduled = get<{ id: number; status: string }>(
      "SELECT id, status FROM scheduled_messages WHERE id = ?",
      [messageId]
    );
    if (!scheduled) {
      return NextResponse.json({ success: false, error: "Scheduled message not found" }, { status: 404 });
    }

    if (scheduled.status === "sent") {
      return NextResponse.json({ success: false, error: "Sent messages cannot be cancelled" }, { status: 400 });
    }

    run("UPDATE scheduled_messages SET status = 'cancelled' WHERE id = ?", [messageId]);
    return NextResponse.json({ success: true, data: { id: messageId, status: "cancelled" } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
