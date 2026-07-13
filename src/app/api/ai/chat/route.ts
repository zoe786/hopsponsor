import { NextRequest, NextResponse } from "next/server";
import { chatAssistant } from "@/lib/ai";
import type { ChatMessage } from "@/lib/types";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const { messages, style_examples = "" } = await req.json() as {
      messages: ChatMessage[];
      style_examples: string;
    };

    if (!messages?.length) {
      return NextResponse.json({ success: false, error: "messages required" }, { status: 400 });
    }

    const response = await chatAssistant(messages, style_examples);
    return NextResponse.json({ success: true, data: { response } });
  } catch (err) {
    return NextResponse.json({ success: false, error: String(err) }, { status: 500 });
  }
}
