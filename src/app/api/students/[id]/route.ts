import { NextRequest, NextResponse } from "next/server";
import { getStudent, updateStudent, deleteStudent } from "@/lib/db";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const student = getStudent(Number(id));
    if (!student) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    return NextResponse.json({ success: true, data: student });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const {
      name, age, contact_info = "", address = "",
      grade_id = null, sponsor_id = null, auto_send = true, notes = "",
    } = await req.json();
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }
    updateStudent(
      Number(id), name.trim(), Number(age), contact_info, address,
      grade_id ? Number(grade_id) : null,
      sponsor_id ? Number(sponsor_id) : null,
      Boolean(auto_send), notes
    );
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    deleteStudent(Number(id));
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
