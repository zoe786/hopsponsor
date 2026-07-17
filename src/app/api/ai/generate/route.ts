import { NextRequest, NextResponse } from "next/server";
import { generateMessage, describeImage } from "@/lib/ai";
import { query } from "@/lib/db-utils";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const contentType = req.headers.get("content-type") ?? "";
    let prompt = "";
    let imageFile: File | null = null;

    if (contentType.includes("multipart/form-data")) {
      const formData = await req.formData();
      prompt = String(formData.get("prompt") ?? "");
      imageFile = formData.get("image") as File | null;
    } else {
      const body = await req.json();
      prompt = String(body.prompt ?? "");
    }

    if (!prompt?.trim()) {
      return NextResponse.json({ success: false, error: "prompt is required" }, { status: 400 });
    }

    const styles = query<{ message: string }>(
      "SELECT message FROM style_library ORDER BY golden_example DESC, id DESC LIMIT 20"
    );
    const styleExamples = styles.map((s) => s.message).join("\n\n");

    let imageDescription = "";
    if (imageFile && imageFile.size > 0) {
      const buffer = Buffer.from(await imageFile.arrayBuffer());
      imageDescription = await describeImage(buffer);
    }

    const draft = await generateMessage(prompt, styleExamples, imageDescription);
    return NextResponse.json({ success: true, data: { draft, imageDescription } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
