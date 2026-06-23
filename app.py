from database import (
    initialize_database,
    add_sponsor,
    add_style,
    add_message,
    sponsors_to_dataframe,
    styles_to_dataframe,
    messages_to_dataframe,
    add_scheduled_message,
    scheduled_messages_to_dataframe,
    update_scheduled_message_status,
    get_grades,
    add_student,
    get_students,
    get_student,
    update_student_auto_send,
    get_sponsor,
    add_report,
    get_reports,
    update_report_sent,
    get_students_by_name_fragment,
    update_sponsor,
    delete_sponsor,
    update_student,
    delete_student
)

from ai_helper import (
    generate_message,
    chat_assistant,
    describe_image,
    send_email,
    send_whatsapp,
    send_email_with_attachment,
    match_files_to_students
)
import streamlit as st
import datetime
import os
import pandas as pd

# Ensure data folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)

initialize_database()

st.set_page_config(
    page_title="Sponsor Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# THEME TOGGLE (Dark/Light)
# ============================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# ============================================
# CUSTOM CSS (Dark/Light compatible)
# ============================================
if st.session_state.theme == "dark":
    bg_color = "#0F172A"
    card_bg = "#1E293B"
    text_color = "#E2E8F0"
    text_secondary = "#94A3B8"
    border_color = "#334155"
    input_bg = "#1E293B"
    hover_bg = "#334155"
    table_header = "#1E293B"
else:
    bg_color = "#F8FAFC"
    card_bg = "#FFFFFF"
    text_color = "#0F172A"
    text_secondary = "#64748B"
    border_color = "#E2E8F0"
    input_bg = "#FFFFFF"
    hover_bg = "#F1F5F9"
    table_header = "#F8FAFC"

st.markdown(f"""
<style>
    /* ----- Global ----- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background: {bg_color};
        color: {text_color};
    }}
    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }}
    /* ----- Sidebar ----- */
    .css-1d391kg {{
        background: #0F172A !important;
        padding-top: 1rem;
    }}
    .css-1d391kg .css-1aumxhk {{
        color: #FFFFFF !important;
    }}
    .css-1d391kg .css-1aumxhk:hover {{
        background: rgba(37, 99, 235, 0.2);
        border-radius: 8px;
    }}
    .sidebar-logo {{
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        padding: 0.5rem 0 1.5rem 0.5rem;
        letter-spacing: -0.02em;
    }}
    .sidebar-logo span {{
        color: #2563EB;
    }}
    .sidebar-stats {{
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        color: #FFFFFF;
    }}
    .sidebar-stats .stat-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
    }}
    .sidebar-stats .stat-number {{
        font-size: 1.2rem;
        font-weight: 600;
    }}
    /* ----- Cards ----- */
    .metric-card {{
        background: {card_bg};
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid {border_color};
        transition: all 0.2s;
        height: 100%;
    }}
    .metric-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-color: #2563EB;
    }}
    .metric-card .metric-icon {{
        font-size: 1.8rem;
        margin-bottom: 0.25rem;
    }}
    .metric-card .metric-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {text_color};
        line-height: 1.2;
    }}
    .metric-card .metric-label {{
        font-size: 0.875rem;
        color: {text_secondary};
        font-weight: 500;
        margin-top: 0.25rem;
    }}
    .metric-card .metric-trend {{
        font-size: 0.8rem;
        font-weight: 500;
        color: #10B981;
        background: #ECFDF5;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }}
    /* ----- Editable Table ----- */
    .dataframe-container {{
        background: {card_bg};
        border-radius: 12px;
        border: 1px solid {border_color};
        overflow: auto;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .dataframe-container table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }}
    .dataframe-container th {{
        background: {table_header};
        font-weight: 600;
        color: {text_color};
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 2px solid {border_color};
        position: sticky;
        top: 0;
        z-index: 10;
    }}
    .dataframe-container td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid {border_color};
        color: {text_color};
    }}
    .dataframe-container tr:hover td {{
        background: {hover_bg};
    }}
    .dataframe-container tr:last-child td {{
        border-bottom: none;
    }}
    /* ----- Buttons ----- */
    .stButton button {{
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }}
    .stButton button[kind="primary"] {{
        background: #2563EB;
        border-color: #2563EB;
        color: white;
    }}
    .stButton button[kind="primary"]:hover {{
        background: #1D4ED8;
        border-color: #1D4ED8;
    }}
    .stButton button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    /* ----- Theme Toggle ----- */
    .theme-toggle {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        background: {card_bg};
        border-radius: 8px;
        border: 1px solid {border_color};
        cursor: pointer;
    }}
    /* ----- Hierarchy Navigation ----- */
    .hierarchy-item {{
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid {border_color};
        background: {card_bg};
        margin-bottom: 0.5rem;
    }}
    .hierarchy-item:hover {{
        background: {hover_bg};
        border-color: #2563EB;
    }}
    .hierarchy-item.active {{
        border-color: #2563EB;
        background: #DBEAFE;
    }}
    /* ----- Form Styles ----- */
    .form-container {{
        background: {card_bg};
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid {border_color};
        margin: 1rem 0;
    }}
    .form-container h3 {{
        margin-top: 0;
        margin-bottom: 1rem;
        color: {text_color};
        border-bottom: 2px solid {border_color};
        padding-bottom: 0.5rem;
    }}
    /* ----- Section Headers ----- */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {text_color};
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .section-subheader {{
        font-size: 0.9rem;
        color: {text_secondary};
        margin-bottom: 1.5rem;
    }}
    /* ----- Empty States ----- */
    .empty-state {{
        text-align: center;
        padding: 3rem 1rem;
        color: {text_secondary};
    }}
    .empty-state .empty-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
    }}
    .empty-state .empty-text {{
        font-size: 1.1rem;
        font-weight: 500;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        🤝 <span>Sponsor</span>AI
    </div>
    """, unsafe_allow_html=True)

    sponsors_df = sponsors_to_dataframe()
    students_df = get_students()
    messages_df = messages_to_dataframe()
    pending_schedules = scheduled_messages_to_dataframe(status="pending")

    st.markdown(f"""
    <div class="sidebar-stats">
        <div class="stat-label">Total Sponsors</div>
        <div class="stat-number">{len(sponsors_df)}</div>
    </div>
    <div class="sidebar-stats">
        <div class="stat-label">Total Students</div>
        <div class="stat-number">{len(students_df)}</div>
    </div>
    <div class="sidebar-stats">
        <div class="stat-label">Pending Schedules</div>
        <div class="stat-number">{len(pending_schedules)}</div>
    </div>
    """, unsafe_allow_html=True)

    # Theme toggle
    theme_label = "🌙 Dark" if st.session_state.theme == "light" else "☀️ Light"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()

    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Sponsors", "Students", "Assistant", "Message History", "Schedule"],
        index=0,
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("v2.0 • SaaS Edition")

# ============================================
# PAGE ROUTING
# ============================================

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Overview of your sponsor ecosystem</div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-number">{len(sponsors_df)}</div>
            <div class="metric-label">Sponsors</div>
            <div class="metric-trend">+{len(sponsors_df)} total</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🎓</div>
            <div class="metric-number">{len(students_df)}</div>
            <div class="metric-label">Students</div>
            <div class="metric-trend">+{len(students_df)} total</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        reports_count = len(get_reports())
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📄</div>
            <div class="metric-number">{reports_count}</div>
            <div class="metric-label">Reports Uploaded</div>
            <div class="metric-trend">+{reports_count} total</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        sent_count = len(messages_df[messages_df["Status"] == "Sent"]) if not messages_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">✉️</div>
            <div class="metric-number">{sent_count}</div>
            <div class="metric-label">Messages Sent</div>
            <div class="metric-trend">+{sent_count} total</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        pending_count = len(pending_schedules)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⏳</div>
            <div class="metric-number">{pending_count}</div>
            <div class="metric-label">Scheduled</div>
            <div class="metric-trend">{pending_count} pending</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Recent Activity")
    if not messages_df.empty:
        st.dataframe(messages_df.head(5)[["Date", "Recipient", "Channel", "Status"]], use_container_width=True)
    else:
        st.info("No recent activity yet.")

# ---------- SPONSORS (Editable Excel-like Table) ----------
elif page == "Sponsors":
    st.markdown('<div class="section-header">👥 Sponsors</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Editable table – click any cell to modify</div>', unsafe_allow_html=True)

    # Get data
    df = sponsors_to_dataframe()

    # Add new sponsor
    with st.expander("➕ Add New Sponsor", expanded=False):
        with st.form("add_sponsor_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                company = st.text_input("Company")
            with col2:
                email = st.text_input("Email")
                whatsapp = st.text_input("WhatsApp")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add Sponsor"):
                if name:
                    add_sponsor(name, company, whatsapp, email, notes)
                    st.success("Sponsor added!")
                    st.rerun()
                else:
                    st.warning("Name is required.")

    # Editable table using st.data_editor
    if not df.empty:
        # Drop ID column from editing view
        display_df = df.drop(columns=["ID"])

        # Show editable table
        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            num_rows="dynamic",
            key="sponsor_editor",
            hide_index=True,
            column_config={
                "Name": st.column_config.TextColumn("Name", required=True),
                "Company": st.column_config.TextColumn("Company"),
                "Email": st.column_config.TextColumn("Email"),
                "WhatsApp": st.column_config.TextColumn("WhatsApp"),
                "Notes": st.column_config.TextColumn("Notes"),
            }
        )

        # Save changes button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save All Changes", use_container_width=True):
                # We need to update the database with the edited data
                # For each row, find the ID and update
                for idx, row in edited_df.iterrows():
                    # Find matching ID from original df by comparing Name
                    original_row = df[df["Name"] == row["Name"]]
                    if not original_row.empty:
                        sponsor_id = original_row.iloc[0]["ID"]
                        update_sponsor(
                            sponsor_id,
                            row["Name"],
                            row["Company"],
                            row["WhatsApp"],
                            row["Email"],
                            row["Notes"]
                        )
                st.success("All changes saved!")
                st.rerun()

        with col2:
            # Delete selected row
            delete_name = st.selectbox("Delete sponsor:", ["None"] + df["Name"].tolist())
            if delete_name != "None":
                if st.button("🗑️ Delete Selected", use_container_width=True):
                    if st.checkbox("Confirm deletion?"):
                        sponsor = df[df["Name"] == delete_name].iloc[0]
                        delete_sponsor(sponsor["ID"])
                        st.success(f"Deleted {delete_name}!")
                        st.rerun()
    else:
        st.info("No sponsors yet. Add one above.")

# ---------- STUDENTS (Hierarchy: Grade → Student → Form) ----------
elif page == "Students":
    st.markdown('<div class="section-header">🎓 Students</div>', unsafe_allow_html=True)

    # Session state for navigation
    if "selected_grade" not in st.session_state:
        st.session_state.selected_grade = None
    if "selected_student" not in st.session_state:
        st.session_state.selected_student = None

    # Get data
    students_df = get_students()
    grades = get_grades()

    # ============ STEP 1: GRADE SELECTION ============
    if st.session_state.selected_grade is None:
        st.markdown('<div class="section-subheader">Select a grade to view students</div>', unsafe_allow_html=True)

        # Show grades as cards
        grades_list = grades["name"].tolist()
        cols = st.columns(4)
        for i, grade in enumerate(grades_list):
            with cols[i % 4]:
                student_count = len(students_df[students_df["grade_name"] == grade])
                st.markdown(f"""
                <div class="hierarchy-item" onclick="st.rerun()">
                    <div style="font-size:1.2rem;font-weight:600;">{grade}</div>
                    <div style="font-size:0.9rem;color:{text_secondary};">{student_count} students</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"📂 {grade}", key=f"grade_{grade}"):
                    st.session_state.selected_grade = grade
                    st.session_state.selected_student = None
                    st.rerun()

        # Also show "Add New Student" button
        with st.expander("➕ Add New Student", expanded=False):
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name")
                    age = st.number_input("Age", min_value=1, max_value=100, step=1)
                with col2:
                    grade_name = st.selectbox("Grade", grades["name"].tolist())
                    grade_id = grades[grades["name"] == grade_name]["id"].iloc[0]
                contact_info = st.text_input("Contact Info (phone/email)")
                address = st.text_area("Address")
                sponsors_df = sponsors_to_dataframe()
                sponsor_options = ["None"] + sponsors_df["Name"].tolist()
                sponsor_name = st.selectbox("Sponsor", sponsor_options)
                sponsor_id = None
                if sponsor_name != "None":
                    sponsor_id = sponsors_df[sponsors_df["Name"] == sponsor_name]["ID"].iloc[0]
                auto_send = st.checkbox("Auto‑send reports to sponsor", value=True)
                notes = st.text_area("Notes (optional)")
                if st.form_submit_button("Add Student"):
                    if name:
                        code = add_student(name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
                        st.success(f"Student {name} added with ID {code}!")
                        st.rerun()
                    else:
                        st.warning("Please enter a name.")

    # ============ STEP 2: STUDENT SELECTION ============
    elif st.session_state.selected_grade is not None and st.session_state.selected_student is None:
        grade = st.session_state.selected_grade

        # Back button
        if st.button("← Back to Grades"):
            st.session_state.selected_grade = None
            st.rerun()

        st.markdown(f'<div class="section-header">📚 {grade}</div>', unsafe_allow_html=True)

        # Filter students by grade
        grade_students = students_df[students_df["grade_name"] == grade]

        if not grade_students.empty:
            # Show as cards
            cols = st.columns(3)
            for i, (idx, student) in enumerate(grade_students.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="hierarchy-item">
                        <div style="font-size:1.1rem;font-weight:600;">{student['name']}</div>
                        <div style="font-size:0.85rem;color:{text_secondary};">{student['student_code']}</div>
                        <div style="font-size:0.85rem;color:{text_secondary};">Sponsor: {student['sponsor_name'] if student['sponsor_name'] else 'None'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"👤 {student['name']}", key=f"student_{student['id']}"):
                        st.session_state.selected_student = student['id']
                        st.rerun()
        else:
            st.info(f"No students in {grade}. Add one below.")

            with st.expander("➕ Add Student to this Grade", expanded=True):
                with st.form("add_student_grade_form"):
                    name = st.text_input("Full Name")
                    age = st.number_input("Age", min_value=1, max_value=100, step=1)
                    contact_info = st.text_input("Contact Info")
                    address = st.text_area("Address")
                    grade_id = grades[grades["name"] == grade]["id"].iloc[0]
                    sponsors_df = sponsors_to_dataframe()
                    sponsor_options = ["None"] + sponsors_df["Name"].tolist()
                    sponsor_name = st.selectbox("Sponsor", sponsor_options)
                    sponsor_id = None
                    if sponsor_name != "None":
                        sponsor_id = sponsors_df[sponsors_df["Name"] == sponsor_name]["ID"].iloc[0]
                    auto_send = st.checkbox("Auto‑send reports", value=True)
                    notes = st.text_area("Notes")
                    if st.form_submit_button("Add Student"):
                        if name:
                            code = add_student(name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
                            st.success(f"Student {name} added!")
                            st.rerun()

    # ============ STEP 3: STUDENT FORM ============
    elif st.session_state.selected_student is not None:
        student_id = st.session_state.selected_student
        student = get_student(student_id)

        if student is not None:
            # Back buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Students"):
                    st.session_state.selected_student = None
                    st.rerun()
            with col2:
                if st.button("← Back to Grades"):
                    st.session_state.selected_grade = None
                    st.session_state.selected_student = None
                    st.rerun()

            # ============ STUDENT FORM (Admission-style) ============
            st.markdown(f"""
            <div class="form-container">
                <h3>📋 Student Profile – {student['name']}</h3>
                <p style="color:{text_secondary};">Student Code: {student['student_code']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Edit form
            with st.form("student_profile_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name", value=student["name"])
                    age = st.number_input("Age", value=student["age"], min_value=1, max_value=100, step=1)
                    contact_info = st.text_input("Contact Info", value=student["contact_info"])
                with col2:
                    grades = get_grades()
                    grade_options = grades["name"].tolist()
                    current_grade = student["grade_name"]
                    grade_idx = grade_options.index(current_grade) if current_grade in grade_options else 0
                    grade_name = st.selectbox("Grade", grade_options, index=grade_idx)
                    grade_id = grades[grades["name"] == grade_name]["id"].iloc[0]

                    sponsors_df = sponsors_to_dataframe()
                    sponsor_options = ["None"] + sponsors_df["Name"].tolist()
                    current_sponsor = student["sponsor_name"] if student["sponsor_name"] else "None"
                    sponsor_idx = sponsor_options.index(current_sponsor) if current_sponsor in sponsor_options else 0
                    sponsor_name = st.selectbox("Sponsor", sponsor_options, index=sponsor_idx)
                    sponsor_id = None if sponsor_name == "None" else sponsors_df[sponsors_df["Name"] == sponsor_name]["ID"].iloc[0]

                address = st.text_area("Address", value=student["address"])
                auto_send = st.checkbox("Auto‑send reports to sponsor", value=bool(student["auto_send"]))
                notes = st.text_area("Notes", value=student["notes"])

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        if st.checkbox("Confirm changes?"):
                            update_student(
                                student_id, name, age, contact_info, address,
                                grade_id, sponsor_id, auto_send, notes
                            )
                            st.success("Student updated!")
                            st.rerun()
                with col2:
                    if st.form_submit_button("🗑️ Delete Student", use_container_width=True):
                        if st.checkbox("Confirm deletion? This cannot be undone."):
                            delete_student(student_id)
                            st.success("Student deleted!")
                            st.session_state.selected_student = None
                            st.rerun()
                with col3:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.selected_student = None
                        st.rerun()

            # ============ REPORTS SECTION ============
            st.divider()
            st.subheader("📄 Reports")

            # Upload report
            uploaded_file = st.file_uploader(
                "Upload a report for this student",
                type=["pdf", "png", "jpg", "jpeg", "docx"],
                key=f"report_{student_id}"
            )
            if uploaded_file:
                if st.button("Upload and Send to Sponsor"):
                    os.makedirs("data/reports", exist_ok=True)
                    ext = uploaded_file.name.split('.')[-1]
                    safe_name = f"{student['student_code']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    file_path = os.path.join("data/reports", safe_name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    report_id = add_report(student_id, file_path, uploaded_file.name)

                    if student["auto_send"] and student["sponsor_id"]:
                        sponsor = get_sponsor(student["sponsor_id"])
                        if sponsor and sponsor.get("email"):
                            body = f"""
Dear {sponsor['name']},

A new report for {student['name']} (Grade: {student['grade_name']}) is now available.

Student Details:
- Age: {student['age']}
- Contact: {student['contact_info']}
- Address: {student['address']}

Please see the attached report.
"""
                            result = send_email_with_attachment(
                                sponsor["email"],
                                f"Report for {student['name']}",
                                body,
                                file_path
                            )
                            if result.get("success"):
                                update_report_sent(report_id, sponsor["email"])
                                st.success("Report uploaded and sent to sponsor!")
                            else:
                                st.warning(f"Report uploaded but email failed: {result.get('error')}")
                    else:
                        st.success("Report uploaded (auto-send disabled or no sponsor assigned).")

            # Show previous reports
            reports = get_reports(student_id)
            if not reports.empty:
                st.subheader("Previous Reports")
                st.dataframe(reports[["file_name", "upload_date", "message_sent", "sent_to"]], use_container_width=True)

# ---------- ASSISTANT ----------
elif page == "Assistant":
    st.markdown('<div class="section-header">🤖 Assistant</div>', unsafe_allow_html=True)

    mode = st.radio("Mode", ["Chat", "Draft"], horizontal=True, index=0)

    uploaded_image = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg"], key="assistant_img")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = "🧑" if role == "user" else "🤖"
        css_class = "user" if role == "user" else "assistant"
        with st.container():
            st.markdown(f"""
            <div class="chat-message {css_class}">
                <div class="avatar">{avatar}</div>
                <div class="bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if msg.get("is_draft") and not msg.get("processed"):
                channel = st.selectbox("Send via:", ["Email", "WhatsApp"], key=f"ch_{msg['id']}")
                sponsors_df = sponsors_to_dataframe()
                recipient = st.selectbox("Recipient", ["Select..."] + sponsors_df["Name"].tolist(), key=f"rec_{msg['id']}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("✅ Send Now", key=f"send_{msg['id']}"):
                        if recipient != "Select...":
                            sponsor = sponsors_df[sponsors_df["Name"] == recipient].iloc[0]
                            email = sponsor["Email"]
                            if channel == "Email" and email:
                                res = send_email(email, "Message", msg["content"])
                                if res.get("success"):
                                    add_message(str(datetime.date.today()), recipient, "Email", "Outbound", msg["content"], "Sent")
                                    msg["processed"] = True
                                    msg["content"] += "\n\n✅ Sent."
                                    st.rerun()
                        else:
                            st.warning("Select a recipient.")
                with col2:
                    if st.button("📅 Schedule", key=f"sch_{msg['id']}"):
                        if recipient != "Select...":
                            st.session_state["sched_draft"] = msg["content"]
                            st.session_state["sched_recipient"] = recipient
                            st.session_state["sched_channel"] = channel
                            st.session_state["sched_id"] = msg["id"]
                            st.rerun()
                with col3:
                    if st.button("💾 Save Draft", key=f"save_{msg['id']}"):
                        add_message(str(datetime.date.today()), recipient if recipient != "Select..." else "Draft", channel, "Outbound", msg["content"], "Draft")
                        msg["processed"] = True
                        msg["content"] += "\n\n📝 Saved as draft."
                        st.rerun()
                with col4:
                    if st.button("❌ Reject", key=f"rej_{msg['id']}"):
                        msg["processed"] = True
                        msg["content"] += "\n\n❌ Rejected."
                        st.rerun()

    if "sched_draft" in st.session_state:
        with st.expander("📅 Schedule", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                send_date = st.date_input("Date", value=datetime.date.today() + datetime.timedelta(days=1))
            with col2:
                send_time = st.time_input("Time", value=datetime.datetime.now().time())
            send_dt = datetime.datetime.combine(send_date, send_time)
            if st.button("Confirm Schedule"):
                add_scheduled_message(
                    st.session_state["sched_recipient"],
                    st.session_state["sched_channel"],
                    st.session_state["sched_draft"],
                    send_dt.isoformat()
                )
                for m in st.session_state.messages:
                    if m.get("id") == st.session_state["sched_id"]:
                        m["processed"] = True
                        m["content"] += f"\n\n📅 Scheduled for {send_dt.strftime('%Y-%m-%d %H:%M')}."
                        break
                del st.session_state["sched_draft"]
                del st.session_state["sched_recipient"]
                del st.session_state["sched_channel"]
                del st.session_state["sched_id"]
                st.rerun()
            if st.button("Cancel"):
                for k in ["sched_draft", "sched_recipient", "sched_channel", "sched_id"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    with st.container():
        prompt = st.chat_input("Type your message...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            if mode == "Chat":
                styles_df = styles_to_dataframe()
                style_text = "\n".join(styles_df["Message"].astype(str)) if not styles_df.empty else ""
                img_data = uploaded_image.read() if uploaded_image else None
                with st.spinner("Thinking..."):
                    response = chat_assistant(st.session_state.messages, style_text, img_data)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            else:
                img_desc = ""
                if uploaded_image:
                    img_desc = describe_image(uploaded_image.read())
                styles_df = styles_to_dataframe()
                style_text = "\n".join(styles_df["Message"].astype(str)) if not styles_df.empty else ""
                draft = generate_message(prompt, style_text, img_desc)
                draft_id = len(st.session_state.messages)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": draft,
                    "is_draft": True,
                    "processed": False,
                    "id": draft_id
                })
                st.rerun()

# ---------- MESSAGE HISTORY ----------
elif page == "Message History":
    st.markdown('<div class="section-header">📜 Message History</div>', unsafe_allow_html=True)
    df = messages_to_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No messages yet.")

# ---------- SCHEDULE ----------
elif page == "Schedule":
    st.markdown('<div class="section-header">⏳ Scheduled Messages</div>', unsafe_allow_html=True)

    if st.button("📤 Send Due Now"):
        try:
            from worker import send_due_messages
            send_due_messages()
            st.success("Due messages sent!")
            st.rerun()
        except:
            st.error("Worker not found.")

    st.divider()

    with st.expander("➕ New Schedule"):
        with st.form("new_schedule"):
            sponsors_df = sponsors_to_dataframe()
            recipient = st.selectbox("Recipient", ["Select..."] + sponsors_df["Name"].tolist())
            channel = st.selectbox("Channel", ["Email", "WhatsApp"])
            message = st.text_area("Message")
            col1, col2 = st.columns(2)
            with col1:
                send_date = st.date_input("Date", value=datetime.date.today() + datetime.timedelta(days=1))
            with col2:
                send_time = st.time_input("Time", value=datetime.datetime.now().time())
            send_dt = datetime.datetime.combine(send_date, send_time)
            if st.form_submit_button("Schedule"):
                if recipient != "Select..." and message:
                    add_scheduled_message(recipient, channel, message, send_dt.isoformat())
                    st.success("Scheduled!")
                    st.rerun()

    st.subheader("📋 Pending")
    pending_df = scheduled_messages_to_dataframe(status="pending")
    if not pending_df.empty:
        for _, row in pending_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{row['Recipient']}** – {row['Message'][:60]}...")
                col1.caption(f"📅 {row['Send Time']}")
                with col2:
                    if st.button("Send Now", key=f"send_{row['ID']}"):
                        sponsor = sponsors_df[sponsors_df["Name"] == row["Recipient"]].iloc[0]
                        email = sponsor["Email"]
                        if row["Channel"] == "Email" and email:
                            res = send_email(email, "Scheduled", row["Message"])
                            if res.get("success"):
                                add_message(str(datetime.date.today()), row["Recipient"], "Email", "Outbound", row["Message"], "Sent")
                                update_scheduled_message_status(row["ID"], "sent")
                                st.rerun()
                with col3:
                    if st.button("Cancel", key=f"cancel_{row['ID']}"):
                        update_scheduled_message_status(row["ID"], "cancelled")
                        st.rerun()
    else:
        st.info("No pending schedules.")

    with st.expander("📜 History"):
        all_df = scheduled_messages_to_dataframe(status=None)
        if not all_df.empty:
            st.dataframe(all_df[all_df["Status"] != "pending"], use_container_width=True)