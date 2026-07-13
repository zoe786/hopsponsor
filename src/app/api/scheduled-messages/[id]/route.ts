import { NextRequest, NextResponse } from "next/server";
import { updateScheduledMessageStatus } from "@/lib/db";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const { status } = await req.json();
    if (!status) return NextResponse.json({ success: false, error: "status required" }, { status: 400 });
    updateScheduledMessageStatus(Number(id), status);
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    updateScheduledMessageStatus(Number(id), "cancelled");
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
