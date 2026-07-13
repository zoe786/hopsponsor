import { NextRequest, NextResponse } from "next/server";
import { matchFilesToStudents } from "@/lib/ai";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const { file_names, student_names } = await req.json() as {
      file_names: string[];
      student_names: string[];
    };

    if (!file_names?.length || !student_names?.length) {
      return NextResponse.json({ success: false, error: "file_names and student_names required" }, { status: 400 });
    }

    const matches = await matchFilesToStudents(file_names, student_names);
    return NextResponse.json({ success: true, data: matches });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
