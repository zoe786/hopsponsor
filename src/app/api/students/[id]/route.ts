import { NextRequest, NextResponse } from "next/server";
import { get, run } from "@/lib/db-utils";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const studentId = Number(id);
  if (!Number.isInteger(studentId) || studentId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid student id" }, { status: 400 });
  }

  try {
    const student = get(
      `SELECT s.id, s.student_code, s.name, s.age, s.contact_info, s.address,
              s.grade_id, s.sponsor_id, s.auto_send, s.notes,
              g.name AS grade_name, sp.name AS sponsor_name,
              sp.email AS sponsor_email, sp.whatsapp AS sponsor_phone
       FROM students s
       LEFT JOIN grades g ON s.grade_id = g.id
       LEFT JOIN sponsors sp ON s.sponsor_id = sp.id
       WHERE s.id = ?`,
      [studentId]
    );
    if (!student) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    return NextResponse.json({ success: true, data: student });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  const studentId = Number(id);
  if (!Number.isInteger(studentId) || studentId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid student id" }, { status: 400 });
  }

  try {
    const {
      name, age, contact_info = "", address = "",
      grade_id = null, sponsor_id = null, auto_send = true, notes = "",
    } = await req.json();
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }
    const result = run(
      `UPDATE students
       SET name = ?, age = ?, contact_info = ?, address = ?, grade_id = ?, sponsor_id = ?, auto_send = ?, notes = ?
       WHERE id = ?`,
      [
        name.trim(),
        Number(age),
        contact_info,
        address,
        grade_id ? Number(grade_id) : null,
        sponsor_id ? Number(sponsor_id) : null,
        Boolean(auto_send) ? 1 : 0,
        notes,
        studentId,
      ]
    );
    if (!result.changes) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const studentId = Number(id);
  if (!Number.isInteger(studentId) || studentId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid student id" }, { status: 400 });
  }

  try {
    const result = run("DELETE FROM students WHERE id = ?", [studentId]);
    if (!result.changes) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
