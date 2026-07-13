import { NextRequest, NextResponse } from "next/server";
import { getCalendarEvents, getScheduledMessages } from "@/lib/db";

export const runtime = "nodejs";

function escapeIcs(value: string) {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/\n/g, "\\n")
    .replace(/,/g, "\\,")
    .replace(/;/g, "\\;");
}

function toIcsDate(value: string) {
  return value.replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
}

export async function GET(req: NextRequest) {
  try {
    const origin = new URL(req.url).origin;
    const events = getCalendarEvents();
    const scheduled = getScheduledMessages("pending");

    const lines = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//HOPe Sponsor Assistant//EN",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
    ];

    for (const event of events) {
      const endTime = event.end_time || new Date(new Date(event.start_time).getTime() + 60 * 60 * 1000).toISOString();
      lines.push(
        "BEGIN:VEVENT",
        `UID:calendar-event-${event.id}@hopsponsor`,
        `DTSTAMP:${toIcsDate(new Date().toISOString())}`,
        `DTSTART:${toIcsDate(event.start_time)}`,
        `DTEND:${toIcsDate(endTime)}`,
        `SUMMARY:${escapeIcs(event.title)}`,
        `DESCRIPTION:${escapeIcs(event.description || "")}`,
        `LOCATION:${escapeIcs(event.location || "")}`,
        `URL:${escapeIcs(origin + "/calendar")}`,
        "END:VEVENT"
      );
    }

    for (const item of scheduled) {
      const endTime = new Date(new Date(item.send_time).getTime() + 30 * 60 * 1000).toISOString();
      const title = `Scheduled ${item.channel} to ${item.recipient_name || item.recipient}`;
      const description = [item.subject ? `Subject: ${item.subject}` : "", item.message].filter(Boolean).join("\n\n");
      lines.push(
        "BEGIN:VEVENT",
        `UID:scheduled-message-${item.id}@hopsponsor`,
        `DTSTAMP:${toIcsDate(new Date().toISOString())}`,
        `DTSTART:${toIcsDate(item.send_time)}`,
        `DTEND:${toIcsDate(endTime)}`,
        `SUMMARY:${escapeIcs(title)}`,
        `DESCRIPTION:${escapeIcs(description)}`,
        `URL:${escapeIcs(origin + "/schedule")}`,
        "END:VEVENT"
      );
    }

    lines.push("END:VCALENDAR");

    return new NextResponse(lines.join("\r\n"), {
      headers: {
        "Content-Type": "text/calendar; charset=utf-8",
        "Content-Disposition": 'inline; filename="hopsponsor-calendar.ics"',
      },
    });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
