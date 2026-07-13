import { NextRequest, NextResponse } from "next/server";
import { addCalendarEvent, getCalendarEvents } from "@/lib/db";

export const runtime = "nodejs";

export async function GET() {
  try {
    return NextResponse.json({ success: true, data: getCalendarEvents() });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
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

    const id = addCalendarEvent(
      title.trim(),
      String(description ?? ""),
      start.toISOString(),
      end ? end.toISOString() : null,
      String(location ?? ""),
      sponsor_id ? Number(sponsor_id) : null,
      student_id ? Number(student_id) : null,
      String(source ?? "manual")
    );

    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
