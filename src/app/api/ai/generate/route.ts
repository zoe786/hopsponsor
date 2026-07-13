import { NextRequest, NextResponse } from "next/server";
import { generateMessage, describeImage } from "@/lib/ai";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const prompt = formData.get("prompt") as string;
    const styleExamples = (formData.get("style_examples") as string) ?? "";
    const imageFile = formData.get("image") as File | null;

    if (!prompt?.trim()) {
      return NextResponse.json({ success: false, error: "prompt is required" }, { status: 400 });
    }

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
