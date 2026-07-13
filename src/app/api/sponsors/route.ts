import { NextRequest, NextResponse } from "next/server";
import { getSponsors, addSponsor } from "@/lib/db";

export const runtime = "nodejs";

export async function GET() {
  try {
    const sponsors = getSponsors();
    return NextResponse.json({ success: true, data: sponsors });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, company = "", whatsapp = "", email = "", notes = "" } = body;
    if (!name?.trim()) {
      return NextResponse.json({ success: false, error: "Name is required" }, { status: 400 });
    }
    const id = addSponsor(name.trim(), company, whatsapp, email, notes);
    return NextResponse.json({ success: true, data: { id } }, { status: 201 });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
