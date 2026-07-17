import { NextRequest, NextResponse } from "next/server";
import { get, run } from "@/lib/db-utils";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const sponsorId = Number(id);
  if (!Number.isInteger(sponsorId) || sponsorId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid sponsor id" }, { status: 400 });
  }

  try {
    const sponsor = get(
      "SELECT id, name, company, whatsapp, email, notes FROM sponsors WHERE id = ?",
      [sponsorId]
    );
    if (!sponsor) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    return NextResponse.json({ success: true, data: sponsor });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  const sponsorId = Number(id);
  if (!Number.isInteger(sponsorId) || sponsorId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid sponsor id" }, { status: 400 });
  }

  try {
    const { name, company = "", whatsapp = "", email = "", notes = "" } = await req.json();
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }
    const result = run(
      `UPDATE sponsors
       SET name = ?, company = ?, whatsapp = ?, email = ?, notes = ?
       WHERE id = ?`,
      [name.trim(), company, whatsapp, email, notes, sponsorId]
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
  const sponsorId = Number(id);
  if (!Number.isInteger(sponsorId) || sponsorId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid sponsor id" }, { status: 400 });
  }

  try {
    const result = run("DELETE FROM sponsors WHERE id = ?", [sponsorId]);
    if (!result.changes) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
