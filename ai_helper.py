from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3
import pandas as pd
import base64
import json
import resend
from twilio.rest import Client

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Generate a message draft (used by the "Draft" mode) ----------
def generate_message(user_prompt, style_examples, image_description=""):
    prompt = f"""
You are a sponsor relationship assistant.

Use the writing examples below to imitate the user's style.

STYLE EXAMPLES:
{style_examples}

USER REQUEST:
{user_prompt}

{image_description}

Write a message draft.
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ---------- Describe an image (for flyers, etc.) ----------
def describe_image(image_data: bytes) -> str:
    base64_image = base64.b64encode(image_data).decode("utf-8")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-vision-preview"
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail, focusing on elements relevant for an event invitation or sponsor communication."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error describing image: {str(e)}"

# ---------- Email sending (without attachment) ----------
def send_email(to: str, subject: str, body: str) -> dict:
    resend.api_key = os.getenv("RESEND_API_KEY")
    try:
        params = {
            "from": "onboarding@resend.dev",  # Replace with your verified domain
            "to": [to],
            "subject": subject,
            "html": body,
        }
        email = resend.Emails.send(params)
        return {"success": True, "id": email.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- Email sending with file attachment ----------
def send_email_with_attachment(to: str, subject: str, body: str, file_path: str) -> dict:
    resend.api_key = os.getenv("RESEND_API_KEY")
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        attachment = {
            "filename": os.path.basename(file_path),
            "content": base64.b64encode(file_data).decode("utf-8")
        }
        params = {
            "from": "onboarding@resend.dev",
            "to": [to],
            "subject": subject,
            "html": body,
            "attachments": [attachment]
        }
        email = resend.Emails.send(params)
        return {"success": True, "id": email.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- WhatsApp sending ----------
def send_whatsapp(to: str, body: str) -> dict:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client_twilio = Client(account_sid, auth_token)
    try:
        # Ensure 'to' includes country code, e.g., "+1234567890"
        message = client_twilio.messages.create(
            body=body,
            from_='whatsapp:+14155238886',  # Twilio sandbox number
            to='whatsapp:' + to
        )
        return {"success": True, "sid": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------- Tools for the Smart Assistant (chat) ----------
def query_database(sql_query: str) -> str:
    try:
        conn = sqlite3.connect("data/sponsor_assistant.db")
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        if df.empty:
            return "No results found."
        return df.to_string(index=False)
    except Exception as e:
        return f"Error executing query: {str(e)}"

def draft_message(user_request: str, style_examples: str, image_description: str = "") -> str:
    prompt = f"""
You are a sponsor relationship assistant.

Use the writing examples below to imitate the user's style.

STYLE EXAMPLES:
{style_examples}

USER REQUEST:
{user_request}

{image_description}

Write a message draft.
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# ---------- Tool definitions (for function calling) ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Run a SELECT SQL query on the sponsors, style_library, or message_history tables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {"type": "string", "description": "The SQL SELECT query to execute."}
                },
                "required": ["sql_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "draft_message",
            "description": "Generate a draft message for sponsors using the user's writing style.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_request": {"type": "string", "description": "The user's request for the message content."},
                    "style_examples": {"type": "string", "description": "The user's writing style examples."},
                    "image_description": {"type": "string", "description": "Optional description of an uploaded image."}
                },
                "required": ["user_request", "style_examples"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_image",
            "description": "Describe the content of an uploaded image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_data": {"type": "string", "description": "Base64-encoded image data."}
                },
                "required": ["image_data"]
            }
        }
    }
]

# ---------- Main chat assistant (for the Chat mode) ----------
def chat_assistant(messages, style_examples, image_data=None):
    image_description = ""
    if image_data:
        try:
            image_description = describe_image(image_data)
        except Exception as e:
            image_description = f"(Error describing image: {str(e)})"

    system_prompt = f"""
You are a helpful assistant for sponsor relationship management.

You have access to the following tools:
1. query_database: to retrieve information from the SQLite database.
2. draft_message: to write a message draft in the user's style.
3. describe_image: to describe uploaded images (already done; description below).

The user's writing style examples are:
{style_examples}

Image description (if any):
{image_description}

Use the tools when needed. Be conversational and helpful.
"""

    api_messages = [{"role": "system", "content": system_prompt}] + messages

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=api_messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
        )

        assistant_message = response.choices[0].message
        api_messages.append(assistant_message.model_dump())

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if func_name == "query_database":
                    sql = arguments.get("sql_query")
                    result = query_database(sql)
                elif func_name == "draft_message":
                    request = arguments.get("user_request")
                    styles = arguments.get("style_examples")
                    img_desc = arguments.get("image_description", "")
                    result = draft_message(request, styles, img_desc)
                elif func_name == "describe_image":
                    result = image_description if image_description else "No image provided."
                else:
                    result = "Unknown function."

                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            continue
        else:
            return assistant_message.content

    return "I couldn't process your request."

# ---------- NEW: AI‑assisted bulk file matching ----------
def match_files_to_students(file_names, student_names):
    """
    Use OpenAI to match file names to student names.
    Returns a dict: file_name -> student_name (or None)
    """
    prompt = f"""
Given the list of student names: {', '.join(student_names)}
and these file names (without extension): {file_names}

Return a JSON object mapping each file name to the most likely student name.
If a file name does not match any student, map it to null.
Only output the JSON, nothing else.
Example:
{{"Areeb_Report": "Areeb", "Sarah_Feb": "Sarah", "Unknown": null}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        mapping = json.loads(response.choices[0].message.content)
        return mapping
    except Exception as e:
        return {"error": str(e)}