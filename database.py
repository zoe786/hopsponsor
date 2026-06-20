import sqlite3
import pandas as pd
import os

DB_NAME = "sponsor_assistant.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    c = conn.cursor()

    # Sponsors
    c.execute("""
    CREATE TABLE IF NOT EXISTS sponsors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        company TEXT,
        whatsapp TEXT,
        email TEXT,
        notes TEXT
    )
    """)

    # Style Library
    c.execute("""
    CREATE TABLE IF NOT EXISTS style_library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        message TEXT,
        golden_example INTEGER
    )
    """)

    # Message History
    c.execute("""
    CREATE TABLE IF NOT EXISTS message_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        recipient TEXT,
        channel TEXT,
        direction TEXT,
        message TEXT,
        status TEXT
    )
    """)

    # Scheduled Messages
    c.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient TEXT,
        channel TEXT,
        message TEXT,
        send_time TEXT,
        status TEXT
    )
    """)

    # Grades
    c.execute("""
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Students
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER,
        contact_info TEXT,
        address TEXT,
        grade_id INTEGER,
        sponsor_id INTEGER,
        auto_send INTEGER DEFAULT 1,
        notes TEXT,
        FOREIGN KEY (grade_id) REFERENCES grades(id),
        FOREIGN KEY (sponsor_id) REFERENCES sponsors(id)
    )
    """)

    # Reports
    c.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_name TEXT,
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
        message_sent INTEGER DEFAULT 0,
        sent_to TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)

    # Indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_messages_recipient ON message_history(recipient)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_messages_date ON message_history(date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sponsors_name ON sponsors(name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_students_sponsor ON students(sponsor_id)")

    # Pre-populate grades
    default_grades = ["Baby Class", "KG 1", "KG 2", "KG 3",
                      "Grade 1", "Grade 2", "Grade 3", "Grade 4",
                      "Grade 5", "Grade 6", "Grade 7",
                      "Form 1", "Form 2", "Form 3", "Form 4",
                      "Form 5", "Form 6",
                      "College", "University"]
    for g in default_grades:
        c.execute("INSERT OR IGNORE INTO grades (name) VALUES (?)", (g,))

    conn.commit()
    conn.close()


# =====================================
# Sponsors
# =====================================

def add_sponsor(name, company, whatsapp, email, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sponsors (name, company, whatsapp, email, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, company, whatsapp, email, notes))
    conn.commit()
    conn.close()


def get_sponsors():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM sponsors ORDER BY name", conn)
    conn.close()
    return df


def sponsors_to_dataframe():
    df = get_sponsors()
    if not df.empty:
        df.columns = ["ID", "Name", "Company", "WhatsApp", "Email", "Notes"]
    return df


def get_sponsor(sponsor_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM sponsors WHERE id = ?", conn, params=(sponsor_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None


def update_sponsor(sponsor_id, name, company, whatsapp, email, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE sponsors
        SET name=?, company=?, whatsapp=?, email=?, notes=?
        WHERE id=?
    """, (name, company, whatsapp, email, notes, sponsor_id))
    conn.commit()
    conn.close()


def delete_sponsor(sponsor_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sponsors WHERE id = ?", (sponsor_id,))
    conn.commit()
    conn.close()


# =====================================
# Style Library
# =====================================

def add_style(category, message, golden_example):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO style_library (category, message, golden_example)
        VALUES (?, ?, ?)
    """, (category, message, int(golden_example)))
    conn.commit()
    conn.close()


def get_styles():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM style_library ORDER BY id DESC", conn)
    conn.close()
    return df


def styles_to_dataframe():
    df = get_styles()
    if not df.empty:
        df.columns = ["ID", "Category", "Message", "Golden Example"]
    return df


# =====================================
# Message History
# =====================================

def add_message(date, recipient, channel, direction, message, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO message_history (date, recipient, channel, direction, message, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, recipient, channel, direction, message, status))
    conn.commit()
    conn.close()


def get_messages():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM message_history ORDER BY id DESC", conn)
    conn.close()
    return df


def messages_to_dataframe():
    df = get_messages()
    if not df.empty:
        df.columns = ["ID", "Date", "Recipient", "Channel", "Direction", "Message", "Status"]
    return df


# =====================================
# Scheduled Messages
# =====================================

def add_scheduled_message(recipient, channel, message, send_time):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO scheduled_messages (recipient, channel, message, send_time, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (recipient, channel, message, send_time))
    conn.commit()
    conn.close()


def get_scheduled_messages(status="pending"):
    conn = get_connection()
    query = "SELECT * FROM scheduled_messages"
    if status:
        query += " WHERE status = ?"
        df = pd.read_sql_query(query, conn, params=(status,))
    else:
        df = pd.read_sql_query(query + " ORDER BY send_time", conn)
    conn.close()
    return df


def update_scheduled_message_status(msg_id, new_status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE scheduled_messages SET status = ? WHERE id = ?", (new_status, msg_id))
    conn.commit()
    conn.close()


def scheduled_messages_to_dataframe(status="pending"):
    df = get_scheduled_messages(status)
    if not df.empty:
        df.columns = ["ID", "Recipient", "Channel", "Message", "Send Time", "Status"]
    else:
        df = pd.DataFrame(columns=["ID", "Recipient", "Channel", "Message", "Send Time", "Status"])
    return df


# =====================================
# Grades
# =====================================

def get_grades():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM grades ORDER BY name", conn)
    conn.close()
    return df


def grades_to_dataframe():
    df = get_grades()
    if not df.empty:
        df.columns = ["ID", "Grade Name"]
    return df


# =====================================
# Students
# =====================================

def get_next_student_code():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(CAST(SUBSTR(student_code, 5) AS INTEGER)) FROM students")
    max_code = c.fetchone()[0]
    conn.close()
    if max_code is None:
        return "STU-0001"
    return f"STU-{max_code + 1:04d}"


def add_student(name, age, contact_info, address, grade_id, sponsor_id, auto_send=True, notes=""):
    conn = get_connection()
    c = conn.cursor()
    code = get_next_student_code()
    c.execute("""
        INSERT INTO students (student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, name, age, contact_info, address, grade_id, sponsor_id, 1 if auto_send else 0, notes))
    conn.commit()
    conn.close()
    return code


def get_students():
    conn = get_connection()
    query = """
        SELECT s.id, s.student_code, s.name, s.age, s.contact_info, s.address,
               g.name as grade_name, sp.name as sponsor_name, sp.email as sponsor_email, sp.whatsapp as sponsor_phone,
               s.auto_send, s.notes
        FROM students s
        LEFT JOIN grades g ON s.grade_id = g.id
        LEFT JOIN sponsors sp ON s.sponsor_id = sp.id
        ORDER BY s.name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def students_to_dataframe():
    df = get_students()
    if not df.empty:
        df.columns = [
            "ID", "Student Code", "Name", "Age", "Contact Info", "Address",
            "Grade", "Sponsor", "Sponsor Email", "Sponsor Phone",
            "Auto Send", "Notes"
        ]
    return df


def get_student(student_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students WHERE id = ?", conn, params=(student_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None


def update_student(student_id, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE students
        SET name=?, age=?, contact_info=?, address=?, grade_id=?, sponsor_id=?, auto_send=?, notes=?
        WHERE id=?
    """, (name, age, contact_info, address, grade_id, sponsor_id, 1 if auto_send else 0, notes, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def update_student_auto_send(student_id, auto_send):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE students SET auto_send = ? WHERE id = ?", (1 if auto_send else 0, student_id))
    conn.commit()
    conn.close()


def get_students_by_name_fragment(fragment):
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, name FROM students WHERE name LIKE ?", conn, params=(f"%{fragment}%",))
    conn.close()
    return df


# =====================================
# Reports
# =====================================

def add_report(student_id, file_path, file_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO reports (student_id, file_path, file_name, upload_date, message_sent, sent_to)
        VALUES (?, ?, ?, datetime('now'), 0, NULL)
    """, (student_id, file_path, file_name))
    conn.commit()
    report_id = c.lastrowid
    conn.close()
    return report_id


def get_reports(student_id=None):
    conn = get_connection()
    if student_id:
        df = pd.read_sql_query("SELECT * FROM reports WHERE student_id = ? ORDER BY upload_date DESC", conn, params=(student_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM reports ORDER BY upload_date DESC", conn)
    conn.close()
    return df


def reports_to_dataframe(student_id=None):
    df = get_reports(student_id)
    if not df.empty:
        df.columns = ["ID", "Student ID", "File Path", "File Name", "Upload Date", "Message Sent", "Sent To"]
    else:
        df = pd.DataFrame(columns=["ID", "Student ID", "File Path", "File Name", "Upload Date", "Message Sent", "Sent To"])
    return df


def update_report_sent(report_id, sent_to):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE reports SET message_sent = 1, sent_to = ? WHERE id = ?", (sent_to, report_id))
    conn.commit()
    conn.close()