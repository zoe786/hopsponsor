import { NextRequest, NextResponse } from "next/server";
import { run } from "@/lib/db-utils";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const styleId = Number(id);
  if (!Number.isInteger(styleId) || styleId <= 0) {
    return NextResponse.json({ success: false, error: "Invalid style id" }, { status: 400 });
  }

  try {
    const result = run("DELETE FROM style_library WHERE id = ?", [styleId]);
    if (!result.changes) {
      return NextResponse.json({ success: false, error: "Not found" }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
