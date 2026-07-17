import { NextResponse } from "next/server";
import { get, query } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function GET() {
  try {
    const counts = get<{
      totalSponsors: number;
      totalStudents: number;
      totalMessages: number;
      pendingScheduled: number;
    }>(
      `SELECT
         (SELECT COUNT(*) FROM sponsors) AS totalSponsors,
         (SELECT COUNT(*) FROM students) AS totalStudents,
         (SELECT COUNT(*) FROM message_history) AS totalMessages,
         (SELECT COUNT(*) FROM scheduled_messages WHERE status = 'pending') AS pendingScheduled`
    );

    const recentMessages = query(
      `SELECT id, date, recipient, channel, direction, message, status
       FROM message_history
       ORDER BY id DESC
       LIMIT 10`
    );

    const messagesByDay = query(
      `SELECT date, COUNT(*) AS count
       FROM message_history
       WHERE date >= date('now', '-30 day')
       GROUP BY date
       ORDER BY date ASC`
    );

    const data = {
      totalSponsors: counts?.totalSponsors ?? 0,
      totalStudents: counts?.totalStudents ?? 0,
      totalMessages: counts?.totalMessages ?? 0,
      pendingScheduled: counts?.pendingScheduled ?? 0,
      recentMessages,
      messagesByDay,
    };
    return NextResponse.json({ success: true, data });
  } catch (err) {
    return NextResponse.json(
      { success: false, error: String(err) },
      { status: 500 }
    );
  }
}
