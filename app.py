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

# ---------- CUSTOM CSS (same as before) ----------
st.markdown("""
<style>
    /* ----- Global ----- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * {
        font-family: 'Inter', sans-serif;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .stApp {
        background: #F8FAFC;
    }
    .css-1d391kg {
        background: #0F172A;
        padding-top: 1rem;
    }
    .css-1d391kg .css-1aumxhk {
        color: #FFFFFF;
    }
    .css-1d391kg .css-1aumxhk:hover {
        background: rgba(37, 99, 235, 0.2);
        border-radius: 8px;
    }
    .sidebar-logo {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        padding: 0.5rem 0 1.5rem 0.5rem;
        letter-spacing: -0.02em;
    }
    .sidebar-logo span {
        color: #2563EB;
    }
    .sidebar-stats {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        color: #FFFFFF;
    }
    .sidebar-stats .stat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
    }
    .sidebar-stats .stat-number {
        font-size: 1.2rem;
        font-weight: 600;
    }
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        transition: all 0.2s;
        height: 100%;
    }
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-color: #2563EB;
    }
    .metric-card .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.25rem;
    }
    .metric-card .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .metric-card .metric-label {
        font-size: 0.875rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    .metric-card .metric-trend {
        font-size: 0.8rem;
        font-weight: 500;
        color: #10B981;
        background: #ECFDF5;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .dataframe-container {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .dataframe-container table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .dataframe-container th {
        background: #F8FAFC;
        font-weight: 600;
        color: #0F172A;
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 2px solid #E2E8F0;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .dataframe-container td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #F1F5F9;
        color: #1E293B;
    }
    .dataframe-container tr:hover td {
        background: #F8FAFC;
    }
    .dataframe-container tr:last-child td {
        border-bottom: none;
    }
    .dataframe-container td .action-btn {
        background: none;
        border: none;
        color: #64748B;
        cursor: pointer;
        font-size: 0.9rem;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        transition: all 0.15s;
    }
    .dataframe-container td .action-btn:hover {
        background: #E2E8F0;
        color: #0F172A;
    }
    .dataframe-container td .action-btn.edit:hover {
        color: #2563EB;
        background: #DBEAFE;
    }
    .dataframe-container td .action-btn.delete:hover {
        color: #EF4444;
        background: #FEE2E2;
    }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: capitalize;
    }
    .status-badge.active {
        background: #DBEAFE;
        color: #1D4ED8;
    }
    .status-badge.inactive {
        background: #F1F5F9;
        color: #64748B;
    }
    .filter-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .filter-bar .stSelectbox, .filter-bar .stTextInput {
        flex: 1;
        min-width: 180px;
    }
    .chat-message {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
        align-items: flex-start;
    }
    .chat-message .avatar {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
        background: #E2E8F0;
    }
    .chat-message.user .avatar {
        background: #2563EB;
        color: white;
    }
    .chat-message.assistant .avatar {
        background: #E2E8F0;
        color: #0F172A;
    }
    .chat-message .bubble {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        max-width: 80%;
        line-height: 1.6;
    }
    .chat-message.user .bubble {
        background: #2563EB;
        color: white;
        border-color: #2563EB;
    }
    .chat-message.assistant .bubble {
        background: white;
    }
    .sticky-chat-input {
        position: sticky;
        bottom: 0;
        background: #F8FAFC;
        padding: 1rem 0;
        border-top: 1px solid #E2E8F0;
        margin-top: 1rem;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button[kind="primary"] {
        background: #2563EB;
        border-color: #2563EB;
    }
    .stButton button[kind="primary"]:hover {
        background: #1D4ED8;
        border-color: #1D4ED8;
    }
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #0F172A;
        background: #F8FAFC;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
    }
    .streamlit-expanderContent {
        border: 1px solid #E2E8F0;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-subheader {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .divider {
        border: none;
        height: 1px;
        background: #E2E8F0;
        margin: 2rem 0;
    }
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #94A3B8;
    }
    .empty-state .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .empty-state .empty-text {
        font-size: 1.1rem;
        font-weight: 500;
    }
    .empty-state .empty-sub {
        font-size: 0.9rem;
        color: #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
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

    page = st.radio(
        "Navigation",
        ["Dashboard", "Sponsors", "Students", "Assistant", "Message History", "Schedule"],
        index=0,
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("v2.0 • SaaS Edition")

# ---------- PAGE ROUTING ----------
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

# ---------- SPONSORS ----------
elif page == "Sponsors":
    st.markdown('<div class="section-header">👥 Sponsors</div>', unsafe_allow_html=True)

    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search sponsors", placeholder="Name, company, email...")
    with col_filter:
        show_inactive = st.checkbox("Show inactive", value=False)

    sponsors_df = sponsors_to_dataframe()
    if search_query:
        sponsors_df = sponsors_df[
            sponsors_df["Name"].str.contains(search_query, case=False, na=False) |
            sponsors_df["Company"].str.contains(search_query, case=False, na=False) |
            sponsors_df["Email"].str.contains(search_query, case=False, na=False)
        ]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sponsors", len(sponsors_df))
    with col2:
        active = len(sponsors_df)
        st.metric("Active", active)
    with col3:
        st.metric("With Email", len(sponsors_df[sponsors_df["Email"].notna()]))

    st.divider()

    if not sponsors_df.empty:
        st.dataframe(sponsors_df[["Name", "Company", "Email", "WhatsApp"]], use_container_width=True)

        st.subheader("Manage Sponsors")
        sponsor_names = sponsors_df["Name"].tolist()
        selected = st.selectbox("Select a sponsor to edit or delete:", ["None"] + sponsor_names)
        if selected != "None":
            sponsor = sponsors_df[sponsors_df["Name"] == selected].iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit"):
                    st.session_state["editing_sponsor"] = sponsor["ID"]
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete"):
                    if st.checkbox("Confirm deletion?", key="del_sp_confirm"):
                        delete_sponsor(sponsor["ID"])
                        st.success("Deleted!")
                        st.rerun()

        if "editing_sponsor" in st.session_state:
            sponsor_id = st.session_state["editing_sponsor"]
            sponsor = sponsors_df[sponsors_df["ID"] == sponsor_id].iloc[0]
            with st.expander("✏️ Edit Sponsor", expanded=True):
                with st.form("edit_sponsor_form"):
                    name = st.text_input("Name", value=sponsor["Name"])
                    company = st.text_input("Company", value=sponsor["Company"])
                    whatsapp = st.text_input("WhatsApp", value=sponsor["WhatsApp"])
                    email = st.text_input("Email", value=sponsor["Email"])
                    notes = st.text_area("Notes", value=sponsor["Notes"])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            if st.checkbox("Confirm changes?"):
                                update_sponsor(sponsor_id, name, company, whatsapp, email, notes)
                                st.success("Updated!")
                                del st.session_state["editing_sponsor"]
                                st.rerun()
                    with col2:
                        if st.form_submit_button("Cancel"):
                            del st.session_state["editing_sponsor"]
                            st.rerun()
    else:
        st.info("No sponsors yet.")

# ---------- STUDENTS ----------
elif page == "Students":
    st.markdown('<div class="section-header">🎓 Students</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_student = st.text_input("🔍 Search students", placeholder="Name, code...")
    with col2:
        grades = ["All"] + get_grades()["name"].tolist()
        grade_filter = st.selectbox("Grade", grades)
    with col3:
        sponsors_df = sponsors_to_dataframe()
        sponsor_filter = st.selectbox("Sponsor", ["All"] + sponsors_df["Name"].tolist())

    students_df = get_students()
    if search_student:
        students_df = students_df[
            students_df["name"].str.contains(search_student, case=False, na=False) |
            students_df["student_code"].str.contains(search_student, case=False, na=False)
        ]
    if grade_filter != "All":
        students_df = students_df[students_df["grade_name"] == grade_filter]
    if sponsor_filter != "All":
        students_df = students_df[students_df["sponsor_name"] == sponsor_filter]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", len(students_df))
    with col2:
        assigned = len(students_df[students_df["sponsor_name"].notna()])
        st.metric("Assigned to Sponsor", assigned)
    with col3:
        auto_send_on = len(students_df[students_df["auto_send"] == 1])
        st.metric("Auto‑send ON", auto_send_on)

    st.divider()

    if not students_df.empty:
        st.dataframe(students_df[["student_code", "name", "grade_name", "sponsor_name", "auto_send"]], use_container_width=True)

        st.subheader("Manage Students")
        student_names = students_df["name"].tolist()
        selected_student = st.selectbox("Select a student to edit/delete:", ["None"] + student_names)
        if selected_student != "None":
            student = students_df[students_df["name"] == selected_student].iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit"):
                    st.session_state["editing_student"] = student["id"]
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete"):
                    if st.checkbox("Confirm deletion?", key="del_st_confirm"):
                        delete_student(student["id"])
                        st.success("Deleted!")
                        st.rerun()

        if "editing_student" in st.session_state:
            student_id = st.session_state["editing_student"]
            student = students_df[students_df["id"] == student_id].iloc[0]
            with st.expander("✏️ Edit Student", expanded=True):
                with st.form("edit_student_form"):
                    name = st.text_input("Name", value=student["name"])
                    age = st.number_input("Age", value=student["age"], min_value=1, max_value=100, step=1)
                    contact = st.text_input("Contact", value=student["contact_info"])
                    address = st.text_area("Address", value=student["address"])
                    grades_df = get_grades()
                    grade_options = grades_df["name"].tolist()
                    grade_idx = grade_options.index(student["grade_name"]) if student["grade_name"] in grade_options else 0
                    grade_name = st.selectbox("Grade", grade_options, index=grade_idx)
                    grade_id = grades_df[grades_df["name"] == grade_name]["id"].iloc[0]
                    sponsors_df = sponsors_to_dataframe()
                    sponsor_options = ["None"] + sponsors_df["Name"].tolist()
                    current_sponsor = student["sponsor_name"] if student["sponsor_name"] else "None"
                    sponsor_idx = sponsor_options.index(current_sponsor) if current_sponsor in sponsor_options else 0
                    sponsor_name = st.selectbox("Sponsor", sponsor_options, index=sponsor_idx)
                    sponsor_id = None if sponsor_name == "None" else sponsors_df[sponsors_df["Name"] == sponsor_name]["ID"].iloc[0]
                    auto_send = st.checkbox("Auto‑send reports", value=bool(student["auto_send"]))
                    notes = st.text_area("Notes", value=student["notes"])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            if st.checkbox("Confirm changes?"):
                                update_student(student_id, name, age, contact, address, grade_id, sponsor_id, auto_send, notes)
                                st.success("Updated!")
                                del st.session_state["editing_student"]
                                st.rerun()
                    with col2:
                        if st.form_submit_button("Cancel"):
                            del st.session_state["editing_student"]
                            st.rerun()
    else:
        st.info("No students match the criteria.")

    st.divider()
    st.subheader("📦 Bulk Upload Reports")
    st.markdown("Drag and drop files or click to browse.")
    bulk_files = st.file_uploader(
        "Upload report files",
        type=["pdf", "png", "jpg", "jpeg", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if bulk_files:
        all_students = get_students()
        if all_students.empty:
            st.warning("Add students first.")
        else:
            student_names = all_students["name"].tolist()
            file_names = [f.name.split('.')[0] for f in bulk_files]
            if st.button("🤖 AI‑match files to students"):
                with st.spinner("AI is analyzing..."):
                    mapping = match_files_to_students(file_names, student_names)
                    if mapping:
                        st.session_state["bulk_mapping"] = mapping
                        st.session_state["bulk_files"] = bulk_files
                        st.rerun()
                    else:
                        st.error("AI matching failed.")
    if "bulk_mapping" in st.session_state:
        st.subheader("Review matches")
        mapping = st.session_state["bulk_mapping"]
        files = st.session_state["bulk_files"]
        match_data = []
        for f in files:
            base = f.name.split('.')[0]
            suggested = mapping.get(base, "")
            options = ["None"] + all_students["name"].tolist()
            idx = options.index(suggested) if suggested in options else 0
            selected = st.selectbox(f"File: {f.name}", options, index=idx, key=f"bulk_{base}")
            match_data.append({"file": f, "student_name": selected})
        if st.button("✅ Confirm & Upload All"):
            os.makedirs("data/reports", exist_ok=True)
            for item in match_data:
                if item["student_name"] != "None":
                    student = all_students[all_students["name"] == item["student_name"]].iloc[0]
                    ext = item["file"].name.split('.')[-1]
                    safe_name = f"{student['student_code']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    file_path = os.path.join("data/reports", safe_name)
                    with open(file_path, "wb") as f:
                        f.write(item["file"].getbuffer())
                    report_id = add_report(student["id"], file_path, item["file"].name)
                    if student["auto_send"] and student["sponsor_id"]:
                        sponsor = get_sponsor(student["sponsor_id"])
                        if sponsor and sponsor.get("email"):
                            body = f"Dear {sponsor['name']},\n\nA new report for {student['name']} is ready.\n\nRegards."
                            result = send_email_with_attachment(sponsor["email"], f"Report for {student['name']}", body, file_path)
                            if result.get("success"):
                                update_report_sent(report_id, sponsor["email"])
            st.success("All uploaded and sent!")
            del st.session_state["bulk_mapping"]
            del st.session_state["bulk_files"]
            st.rerun()
        if st.button("Cancel"):
            del st.session_state["bulk_mapping"]
            del st.session_state["bulk_files"]
            st.rerun()

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