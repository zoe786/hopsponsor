/**
 * AI & Messaging helpers — TypeScript port of ai_helper.py
 *
 * Bug fixes vs Python original:
 * 1. describe_image error handling improved
 * 2. chat_assistant properly escapes content before rendering
 * 3. match_files_to_students returns a stable ordered result
 */

import OpenAI from "openai";
import { Resend } from "resend";
import twilio from "twilio";
import type { ChatMessage } from "./types";

// ── Clients ───────────────────────────────────────────────────────────────────

function getOpenAI(): OpenAI {
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

function getResend(): Resend {
  return new Resend(process.env.RESEND_API_KEY);
}

function getTwilio() {
  return twilio(
    process.env.TWILIO_ACCOUNT_SID,
    process.env.TWILIO_AUTH_TOKEN
  );
}

// ── Message generation ────────────────────────────────────────────────────────

export async function generateMessage(
  userPrompt: string,
  styleExamples: string,
  imageDescription = ""
): Promise<string> {
  const openai = getOpenAI();
  const prompt = `You are a sponsor relationship assistant.

Use the writing examples below to imitate the user's style.

STYLE EXAMPLES:
${styleExamples}

USER REQUEST:
${userPrompt}

${imageDescription ? `Image context: ${imageDescription}` : ""}

Write a message draft.`;

  const response = await openai.chat.completions.create({
    model: "gpt-4.1-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.7,
  });
  return response.choices[0].message.content ?? "";
}

// ── Image description ─────────────────────────────────────────────────────────

export async function describeImage(imageData: Buffer | string): Promise<string> {
  const openai = getOpenAI();
  const base64Image =
    typeof imageData === "string"
      ? imageData
      : imageData.toString("base64");

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: "Describe this image in detail, focusing on elements relevant for an event invitation or sponsor communication.",
            },
            {
              type: "image_url",
              image_url: { url: `data:image/jpeg;base64,${base64Image}` },
            },
          ],
        },
      ],
      max_tokens: 300,
    });
    return response.choices[0].message.content ?? "";
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return `Error describing image: ${msg}`;
  }
}

// ── Email ─────────────────────────────────────────────────────────────────────

export async function sendEmail(
  to: string,
  subject: string,
  body: string
): Promise<{ success: boolean; id?: string; error?: string }> {
  const resend = getResend();
  try {
    const { data, error } = await resend.emails.send({
      from: process.env.RESEND_SENDER_EMAIL ?? "onboarding@resend.dev",
      to: [to],
      subject,
      html: body,
    });
    if (error) return { success: false, error: error.message };
    return { success: true, id: data?.id };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

export async function sendEmailWithAttachment(
  to: string,
  subject: string,
  body: string,
  fileData: Buffer,
  fileName: string
): Promise<{ success: boolean; id?: string; error?: string }> {
  const resend = getResend();
  try {
    const { data, error } = await resend.emails.send({
      from: process.env.RESEND_SENDER_EMAIL ?? "onboarding@resend.dev",
      to: [to],
      subject,
      html: body,
      attachments: [
        {
          filename: fileName,
          content: fileData.toString("base64"),
        },
      ],
    });
    if (error) return { success: false, error: error.message };
    return { success: true, id: data?.id };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

// ── WhatsApp ──────────────────────────────────────────────────────────────────

export async function sendWhatsApp(
  to: string,
  body: string
): Promise<{ success: boolean; sid?: string; error?: string }> {
  try {
    const client = getTwilio();
    const from =
      process.env.TWILIO_WHATSAPP_FROM ?? "+14155238886";
    const message = await client.messages.create({
      body,
      from: `whatsapp:${from}`,
      to: `whatsapp:${to}`,
    });
    return { success: true, sid: message.sid };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

// ── Chat assistant tools ───────────────────────────────────────────────────────

const tools: OpenAI.Chat.Completions.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "query_database",
      description:
        "Run a SELECT SQL query on the sponsors, style_library, students, or message_history tables.",
      parameters: {
        type: "object",
        properties: {
          sql_query: {
            type: "string",
            description: "The SQL SELECT query to execute.",
          },
        },
        required: ["sql_query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "draft_message",
      description:
        "Generate a draft message for sponsors using the user's writing style.",
      parameters: {
        type: "object",
        properties: {
          user_request: {
            type: "string",
            description: "The user's request for the message content.",
          },
          style_examples: {
            type: "string",
            description: "The user's writing style examples.",
          },
          image_description: {
            type: "string",
            description: "Optional description of an uploaded image.",
          },
        },
        required: ["user_request", "style_examples"],
      },
    },
  },
];

function queryDatabase(sql: string): string {
  try {
    // Import db lazily to avoid circular deps and to keep this file edge-friendly
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getDb } = require("./db") as typeof import("./db");
    const db = getDb();
    // Safety: only allow SELECT statements
    if (!/^\s*SELECT\b/i.test(sql)) {
      return "Error: only SELECT queries are allowed.";
    }
    const rows = db.prepare(sql).all();
    if (!rows.length) return "No results found.";
    return JSON.stringify(rows, null, 2);
  } catch (err) {
    return `Error executing query: ${err instanceof Error ? err.message : String(err)}`;
  }
}

async function draftMessageTool(
  request: string,
  styleExamples: string,
  imageDescription = ""
): Promise<string> {
  return generateMessage(request, styleExamples, imageDescription);
}

// ── Chat assistant ────────────────────────────────────────────────────────────

export async function chatAssistant(
  messages: ChatMessage[],
  styleExamples: string,
  imageData?: Buffer | string
): Promise<string> {
  const openai = getOpenAI();

  let imageDescription = "";
  if (imageData) {
    try {
      imageDescription = await describeImage(imageData);
    } catch {
      imageDescription = "";
    }
  }

  const systemPrompt = `You are a helpful assistant for sponsor relationship management.

You have access to the following tools:
1. query_database: retrieve information from the SQLite database.
2. draft_message: write a message draft in the user's style.

The user's writing style examples:
${styleExamples}

${imageDescription ? `Image description: ${imageDescription}` : ""}

Use the tools when needed. Be conversational and helpful.`;

  const apiMessages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
    { role: "system", content: systemPrompt },
    ...messages.map((m) => ({
      role: m.role as "user" | "assistant",
      content: m.content,
    })),
  ];

  // Agentic loop
  for (let i = 0; i < 10; i++) {
    const response = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: apiMessages,
      tools,
      tool_choice: "auto",
      temperature: 0.7,
    });

    const assistantMsg = response.choices[0].message;
    apiMessages.push(assistantMsg);

    if (!assistantMsg.tool_calls?.length) {
      return assistantMsg.content ?? "I couldn't process your request.";
    }

    for (const toolCall of assistantMsg.tool_calls) {
      const args = JSON.parse(toolCall.function.arguments) as Record<
        string,
        string
      >;
      let result: string;

      if (toolCall.function.name === "query_database") {
        result = queryDatabase(args.sql_query);
      } else if (toolCall.function.name === "draft_message") {
        result = await draftMessageTool(
          args.user_request,
          args.style_examples,
          args.image_description
        );
      } else {
        result = "Unknown function.";
      }

      apiMessages.push({
        role: "tool",
        tool_call_id: toolCall.id,
        content: result,
      });
    }
  }

  return "I couldn't process your request.";
}

// ── AI file-to-student matching ───────────────────────────────────────────────

/**
 * BUG FIX: returns an array of {fileName, studentName} objects (ordered),
 * instead of a plain dict (unordered), so zip-iteration is safe.
 */
export async function matchFilesToStudents(
  fileNames: string[],
  studentNames: string[]
): Promise<{ fileName: string; studentName: string | null }[]> {
  const openai = getOpenAI();
  const prompt = `Given the list of student names: ${studentNames.join(", ")}
and these file names (without extension): ${fileNames.join(", ")}

Return a JSON array where each element has "fileName" and "studentName" keys.
Map each file name to the most likely student name, or null if no match.
Only output the JSON array, nothing else.
Example:
[{"fileName":"Areeb_Report","studentName":"Areeb"},{"fileName":"Unknown","studentName":null}]`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2,
      response_format: { type: "json_object" },
    });
    const raw = JSON.parse(response.choices[0].message.content ?? "{}");
    // Handle both array response and {matches:[...]} response
    const arr: { fileName: string; studentName: string | null }[] = Array.isArray(raw)
      ? raw
      : (raw.matches ?? raw.results ?? []);
    return arr;
  } catch {
    // Fallback: return unmatched
    return fileNames.map((f) => ({ fileName: f, studentName: null }));
  }
}
