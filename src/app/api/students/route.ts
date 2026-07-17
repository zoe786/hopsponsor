import { NextRequest, NextResponse } from "next/server";
import { generateNextStudentCode, query, run } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function GET() {
  try {
    const students = query(
      `SELECT s.id, s.student_code, s.name, s.age, s.contact_info, s.address,
              s.grade_id, s.sponsor_id, s.auto_send, s.notes,
              g.name AS grade_name, sp.name AS sponsor_name,
              sp.email AS sponsor_email, sp.whatsapp AS sponsor_phone
       FROM students s
       LEFT JOIN grades g ON s.grade_id = g.id
       LEFT JOIN sponsors sp ON s.sponsor_id = sp.id
       ORDER BY s.name`
    );
    return NextResponse.json({ success: true, data: students });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const {
      name, age = 10, contact_info = "", address = "",
      grade_id = null, sponsor_id = null, auto_send = true, notes = "",
    } = body;
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }

    const code = generateNextStudentCode();

    run(
      `INSERT INTO students
         (student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        code,
        name.trim(),
        Number(age),
        contact_info,
        address,
        grade_id ? Number(grade_id) : null,
        sponsor_id ? Number(sponsor_id) : null,
        Boolean(auto_send) ? 1 : 0,
        notes,
      ]
    );

    return NextResponse.json({ success: true, data: { student_code: code } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
