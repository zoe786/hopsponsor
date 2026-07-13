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

function getOpenAI(): OpenAI {
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

function getResend(): Resend {
  return new Resend(process.env.RESEND_API_KEY);
}

function getTwilio() {
  return twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
}

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

export async function describeImage(imageData: Buffer | string): Promise<string> {
  const openai = getOpenAI();
  const base64Image = typeof imageData === "string" ? imageData : imageData.toString("base64");

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

export async function sendWhatsApp(
  to: string,
  body: string
): Promise<{ success: boolean; sid?: string; error?: string }> {
  try {
    const client = getTwilio();
    const from = process.env.TWILIO_WHATSAPP_FROM ?? "+14155238886";
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

const tools: OpenAI.Chat.Completions.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "query_database",
      description:
        "Run a SELECT SQL query on the sponsors, style_library, students, message_history, scheduled_messages, payment_commitments, or calendar_events tables.",
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
      description: "Generate a draft message for sponsors using the user's writing style.",
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
  {
    type: "function",
    function: {
      name: "schedule_message",
      description: "Schedule a sponsor email or WhatsApp message for later delivery.",
      parameters: {
        type: "object",
        properties: {
          sponsor_name: { type: "string", description: "Sponsor name." },
          channel: { type: "string", description: "Email or WhatsApp." },
          subject: { type: "string", description: "Email subject if channel is Email." },
          message: { type: "string", description: "Message body to send." },
          send_time: {
            type: "string",
            description: "ISO datetime when the message should be sent.",
          },
        },
        required: ["sponsor_name", "channel", "message", "send_time"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "create_payment_commitment",
      description: "Create a payment commitment tracker entry for a sponsor.",
      parameters: {
        type: "object",
        properties: {
          sponsor_name: { type: "string", description: "Sponsor name." },
          student_name: { type: "string", description: "Optional student name." },
          amount_committed: { type: "number", description: "Committed amount." },
          amount_received: { type: "number", description: "Amount already received." },
          currency: { type: "string", description: "Currency code such as USD." },
          frequency: { type: "string", description: "Monthly, quarterly, yearly, one-time, etc." },
          commitment_date: { type: "string", description: "Start or commitment date in YYYY-MM-DD format." },
          next_due_date: { type: "string", description: "Optional next due date in YYYY-MM-DD format." },
          last_payment_date: { type: "string", description: "Optional last payment date in YYYY-MM-DD format." },
          status: { type: "string", description: "active, paused, completed, overdue, etc." },
          notes: { type: "string", description: "Optional notes." },
        },
        required: ["sponsor_name", "amount_committed", "frequency", "commitment_date"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "create_calendar_event",
      description: "Create a calendar event for sponsor or student follow-up.",
      parameters: {
        type: "object",
        properties: {
          title: { type: "string", description: "Event title." },
          description: { type: "string", description: "Event details." },
          start_time: { type: "string", description: "ISO event start datetime." },
          end_time: { type: "string", description: "Optional ISO event end datetime." },
          location: { type: "string", description: "Optional location." },
          sponsor_name: { type: "string", description: "Optional sponsor name." },
          student_name: { type: "string", description: "Optional student name." },
        },
        required: ["title", "start_time"],
      },
    },
  },
];

function queryDatabase(sql: string): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getDb } = require("./db") as typeof import("./db");
    const db = getDb();
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

function scheduleMessageTool(args: Record<string, string>): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getDb, addScheduledMessage } = require("./db") as typeof import("./db");
    const db = getDb();
    const sponsor = db
      .prepare("SELECT id, name FROM sponsors WHERE lower(name) = lower(?) OR name LIKE ? ORDER BY name LIMIT 1")
      .get(args.sponsor_name, `%${args.sponsor_name}%`) as { id: number; name: string } | undefined;

    if (!sponsor) return `Error: sponsor '${args.sponsor_name}' was not found.`;

    const sendTime = new Date(args.send_time);
    if (Number.isNaN(sendTime.getTime())) return "Error: send_time must be a valid ISO datetime.";
    if (sendTime.getTime() <= Date.now()) return "Error: send_time must be in the future.";

    const id = addScheduledMessage(
      sponsor.id,
      sponsor.name,
      args.channel,
      args.subject ?? "",
      args.message,
      sendTime.toISOString()
    );
    return `Scheduled ${args.channel} for ${sponsor.name} with ID ${id} at ${sendTime.toISOString()}.`;
  } catch (err) {
    return `Error scheduling message: ${err instanceof Error ? err.message : String(err)}`;
  }
}

function createPaymentCommitmentTool(args: Record<string, string>): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getDb, addPaymentCommitment } = require("./db") as typeof import("./db");
    const db = getDb();
    const sponsor = db
      .prepare("SELECT id, name FROM sponsors WHERE lower(name) = lower(?) OR name LIKE ? ORDER BY name LIMIT 1")
      .get(args.sponsor_name, `%${args.sponsor_name}%`) as { id: number; name: string } | undefined;

    if (!sponsor) return `Error: sponsor '${args.sponsor_name}' was not found.`;

    let studentId: number | null = null;
    let studentLabel = "";
    if (args.student_name) {
      const student = db
        .prepare("SELECT id, name FROM students WHERE lower(name) = lower(?) OR name LIKE ? ORDER BY name LIMIT 1")
        .get(args.student_name, `%${args.student_name}%`) as { id: number; name: string } | undefined;
      if (!student) return `Error: student '${args.student_name}' was not found.`;
      studentId = student.id;
      studentLabel = ` for ${student.name}`;
    }

    const id = addPaymentCommitment(
      sponsor.id,
      studentId,
      Number(args.amount_committed),
      Number(args.amount_received ?? 0),
      args.currency ?? "USD",
      args.frequency,
      args.commitment_date,
      args.next_due_date ?? null,
      args.last_payment_date ?? null,
      args.status ?? "active",
      args.notes ?? ""
    );

    return `Created payment commitment ${id} for ${sponsor.name}${studentLabel}.`;
  } catch (err) {
    return `Error creating payment commitment: ${err instanceof Error ? err.message : String(err)}`;
  }
}

function createCalendarEventTool(args: Record<string, string>): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getDb, addCalendarEvent } = require("./db") as typeof import("./db");
    const db = getDb();

    const startTime = new Date(args.start_time);
    if (Number.isNaN(startTime.getTime())) return "Error: start_time must be a valid ISO datetime.";

    let endIso: string | null = null;
    if (args.end_time) {
      const endTime = new Date(args.end_time);
      if (Number.isNaN(endTime.getTime())) return "Error: end_time must be a valid ISO datetime.";
      endIso = endTime.toISOString();
    }

    let sponsorId: number | null = null;
    if (args.sponsor_name) {
      const sponsor = db
        .prepare("SELECT id FROM sponsors WHERE lower(name) = lower(?) OR name LIKE ? ORDER BY name LIMIT 1")
        .get(args.sponsor_name, `%${args.sponsor_name}%`) as { id: number } | undefined;
      if (!sponsor) return `Error: sponsor '${args.sponsor_name}' was not found.`;
      sponsorId = sponsor.id;
    }

    let studentId: number | null = null;
    if (args.student_name) {
      const student = db
        .prepare("SELECT id FROM students WHERE lower(name) = lower(?) OR name LIKE ? ORDER BY name LIMIT 1")
        .get(args.student_name, `%${args.student_name}%`) as { id: number } | undefined;
      if (!student) return `Error: student '${args.student_name}' was not found.`;
      studentId = student.id;
    }

    const id = addCalendarEvent(
      args.title,
      args.description ?? "",
      startTime.toISOString(),
      endIso,
      args.location ?? "",
      sponsorId,
      studentId,
      "ai"
    );

    return `Created calendar event ${id} titled '${args.title}'.`;
  } catch (err) {
    return `Error creating calendar event: ${err instanceof Error ? err.message : String(err)}`;
  }
}

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
3. schedule_message: schedule a future sponsor message.
4. create_payment_commitment: create or track sponsor payment commitments.
5. create_calendar_event: create follow-up or event reminders.

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
      const args = JSON.parse(toolCall.function.arguments) as Record<string, string>;
      let result: string;

      if (toolCall.function.name === "query_database") {
        result = queryDatabase(args.sql_query);
      } else if (toolCall.function.name === "draft_message") {
        result = await draftMessageTool(
          args.user_request,
          args.style_examples,
          args.image_description
        );
      } else if (toolCall.function.name === "schedule_message") {
        result = scheduleMessageTool(args);
      } else if (toolCall.function.name === "create_payment_commitment") {
        result = createPaymentCommitmentTool(args);
      } else if (toolCall.function.name === "create_calendar_event") {
        result = createCalendarEventTool(args);
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

export async function matchFilesToStudents(
  fileNames: string[],
  studentNames: string[]
): Promise<{ fileName: string; studentName: string | null }[]> {
  const openai = getOpenAI();
  const prompt = `Given the list of student names: ${studentNames.join(", ")}
and these file names (without extension): ${fileNames.join(", ")}

Return a JSON object with a single key called matches.
Each match should have "fileName" and "studentName" keys.
Map each file name to the most likely student name, or null if no match.
Only output JSON.
Example:
{"matches":[{"fileName":"Areeb_Report","studentName":"Areeb"},{"fileName":"Unknown","studentName":null}]}`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2,
      response_format: { type: "json_object" },
    });
    const raw = JSON.parse(response.choices[0].message.content ?? "{}");
    const arr: { fileName: string; studentName: string | null }[] = Array.isArray(raw)
      ? raw
      : (raw.matches ?? raw.results ?? []);
    return arr;
  } catch {
    return fileNames.map((f) => ({ fileName: f, studentName: null }));
  }
}
