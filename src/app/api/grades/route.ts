import { NextResponse } from "next/server";
import { query } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function GET() {
  try {
    const grades = query(
      `SELECT id, name FROM grades
       ORDER BY CASE name
         WHEN 'No Class' THEN 1
         WHEN 'Baby Class' THEN 2
         WHEN 'KG 1' THEN 3
         WHEN 'KG 2' THEN 4
         WHEN 'KG 3' THEN 5
         WHEN 'Grade 1' THEN 6
         WHEN 'Grade 2' THEN 7
         WHEN 'Grade 3' THEN 8
         WHEN 'Grade 4' THEN 9
         WHEN 'Grade 5' THEN 10
         WHEN 'Grade 6' THEN 11
         WHEN 'Grade 7' THEN 12
         WHEN 'Form 1' THEN 13
         WHEN 'Form 2' THEN 14
         WHEN 'Form 3' THEN 15
         WHEN 'Form 4' THEN 16
         WHEN 'Form 5' THEN 17
         WHEN 'Form 6' THEN 18
         WHEN 'College' THEN 19
         WHEN 'University' THEN 20
         ELSE 999
       END, id`
    );
    return NextResponse.json({ success: true, data: grades });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
