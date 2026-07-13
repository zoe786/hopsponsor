import { NextRequest, NextResponse } from "next/server";
import { deleteCalendarEvent, getCalendarEvent, updateCalendarEvent } from "@/lib/db";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const event = getCalendarEvent(Number(id));
    if (!event) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    return NextResponse.json({ success: true, data: event });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const {
      title,
      description = "",
      start_time,
      end_time = null,
      location = "",
      sponsor_id = null,
      student_id = null,
      source = "manual",
    } = await req.json();

    if (!title?.trim() || !start_time) {
      return NextResponse.json({ success: false, error: "title and start_time are required" }, { status: 400 });
    }

    const start = new Date(start_time);
    const end = end_time ? new Date(end_time) : null;
    if (Number.isNaN(start.getTime()) || (end && Number.isNaN(end.getTime()))) {
      return NextResponse.json({ success: false, error: "Invalid event time" }, { status: 400 });
    }
    if (end && end.getTime() < start.getTime()) {
      return NextResponse.json({ success: false, error: "end_time must be after start_time" }, { status: 400 });
    }

    updateCalendarEvent(
      Number(id),
      title.trim(),
      String(description ?? ""),
      start.toISOString(),
      end ? end.toISOString() : null,
      String(location ?? ""),
      sponsor_id ? Number(sponsor_id) : null,
      student_id ? Number(student_id) : null,
      String(source ?? "manual")
    );
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    deleteCalendarEvent(Number(id));
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
