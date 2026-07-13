import { NextRequest, NextResponse } from "next/server";
import {
  deletePaymentCommitment,
  getPaymentCommitment,
  getSponsor,
  getStudent,
  updatePaymentCommitment,
} from "@/lib/db";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const item = getPaymentCommitment(Number(id));
    if (!item) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    return NextResponse.json({ success: true, data: item });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const {
      sponsor_id,
      student_id = null,
      amount_committed,
      amount_received = 0,
      currency = "USD",
      frequency,
      commitment_date,
      next_due_date = null,
      last_payment_date = null,
      status = "active",
      notes = "",
    } = await req.json();

    if (!sponsor_id || amount_committed === undefined || !frequency || !commitment_date) {
      return NextResponse.json({ success: false, error: "Missing required fields" }, { status: 400 });
    }
    if (!getSponsor(Number(sponsor_id))) {
      return NextResponse.json({ success: false, error: "Sponsor not found" }, { status: 404 });
    }
    if (student_id && !getStudent(Number(student_id))) {
      return NextResponse.json({ success: false, error: "Student not found" }, { status: 404 });
    }

    updatePaymentCommitment(
      Number(id),
      Number(sponsor_id),
      student_id ? Number(student_id) : null,
      Number(amount_committed),
      Number(amount_received),
      String(currency).trim() || "USD",
      String(frequency).trim(),
      String(commitment_date),
      next_due_date ? String(next_due_date) : null,
      last_payment_date ? String(last_payment_date) : null,
      String(status).trim() || "active",
      String(notes ?? "")
    );
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    deletePaymentCommitment(Number(id));
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
