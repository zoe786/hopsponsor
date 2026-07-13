import { NextRequest, NextResponse } from "next/server";
import { addPaymentCommitment, getPaymentCommitments, getSponsor, getStudent } from "@/lib/db";

export const runtime = "nodejs";

export async function GET() {
  try {
    return NextResponse.json({ success: true, data: getPaymentCommitments() });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
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

    const id = addPaymentCommitment(
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

    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
