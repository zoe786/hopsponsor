import { NextRequest, NextResponse } from "next/server";
import { getStudents, addStudent } from "@/lib/db";

export const runtime = "nodejs";

export async function GET() {
  try {
    const students = getStudents();
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
    const code = addStudent(
      name.trim(), Number(age), contact_info, address,
      grade_id ? Number(grade_id) : null,
      sponsor_id ? Number(sponsor_id) : null,
      Boolean(auto_send), notes
    );
    return NextResponse.json({ success: true, data: { student_code: code } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
