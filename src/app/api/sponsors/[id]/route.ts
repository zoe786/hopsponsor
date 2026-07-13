import { NextRequest, NextResponse } from "next/server";
import { getSponsor, updateSponsor, deleteSponsor } from "@/lib/db";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const sponsor = getSponsor(Number(id));
    if (!sponsor) return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    return NextResponse.json({ success: true, data: sponsor });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function PUT(req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    const { name, company = "", whatsapp = "", email = "", notes = "" } = await req.json();
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }
    updateSponsor(Number(id), name.trim(), company, whatsapp, email, notes);
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  try {
    deleteSponsor(Number(id));
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
