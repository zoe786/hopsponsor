# worker.py
import time
import datetime
import os
import sqlite3
import pandas as pd
from ai_helper import send_email, send_whatsapp
from database import get_connection, update_scheduled_message_status, add_message

def send_due_messages():
    """Check scheduled_messages and send any due messages."""
    conn = get_connection()
    now = datetime.datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, recipient, channel, message, send_time
        FROM scheduled_messages
        WHERE status = 'pending' AND send_time <= ?
    """, (now,))
    due = cursor.fetchall()
    conn.close()

    for row in due:
        msg_id, recipient_name, channel, message, send_time = row
        # Try to find the sponsor's email/phone from the sponsors table
        conn2 = get_connection()
        sponsor_df = pd.read_sql_query("SELECT email, whatsapp FROM sponsors WHERE name = ?", conn2, params=(recipient_name,))
        conn2.close()
        if sponsor_df.empty:
            # If not found, we can't send – but we could still log as error?
            print(f"⚠️ Sponsor '{recipient_name}' not found. Skipping message {msg_id}")
            continue

        sponsor = sponsor_df.iloc[0]
        success = False
        if channel == "Email":
            email = sponsor.get("email")
            if email:
                result = send_email(email, f"Scheduled message for {recipient_name}", message)
                if result.get("success"):
                    success = True
                    print(f"✅ Sent email to {recipient_name}")
                else:
                    print(f"❌ Email failed: {result.get('error')}")
            else:
                print(f"⚠️ No email for {recipient_name}")
        elif channel == "WhatsApp":
            phone = sponsor.get("whatsapp")
            if phone:
                result = send_whatsapp(phone, message)
                if result.get("success"):
                    success = True
                    print(f"✅ Sent WhatsApp to {recipient_name}")
                else:
                    print(f"❌ WhatsApp failed: {result.get('error')}")
            else:
                print(f"⚠️ No WhatsApp for {recipient_name}")

        if success:
            # Log to message history
            add_message(
                date=datetime.date.today().isoformat(),
                recipient=recipient_name,
                channel=channel,
                direction="Outbound",
                message=message,
                status="Sent"
            )
            # Update scheduled status
            update_scheduled_message_status(msg_id, "sent")
            print(f"📦 Scheduled message {msg_id} processed.")
        else:
            # Optionally mark as failed or leave as pending to retry
            # We'll leave it pending and it will retry next cycle
            print(f"⏳ Message {msg_id} will retry later.")
        # Avoid hitting the API too fast
        time.sleep(1)

def main():
    print("🚀 Scheduler worker started. Checking every minute...")
    while True:
        try:
            send_due_messages()
        except Exception as e:
            print(f"⚠️ Worker error: {e}")
        time.sleep(60)  # wait 1 minute

if __name__ == "__main__":
    main()