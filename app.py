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
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
    }}
    .sidebar-divider {{
        height: 1px;
        background: rgba(255,255,255,0.1);
        margin: 1rem 0;
    }}
    /* ----- Cards ----- */
    .card {{
        background: {card_bg};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid {border_color};
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }}
    .card:hover {{
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
    }}
    .card-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }}
    .card-icon {{
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }}
    .card-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {text_color};
    }}
    .card-subtitle {{
        font-size: 0.85rem;
        color: {text_secondary};
    }}
    /* ----- Buttons ----- */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .primary-button {{
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .primary-button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }}
    .secondary-button {{
        background: {hover_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
    }}
    .danger-button {{
        background: #EF4444 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
    }}
    /* ----- Data Tables ----- */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {border_color};
    }}
    .stDataFrame thead th {{
        background: {table_header} !important;
        color: {text_color} !important;
        font-weight: 600 !important;
        border-bottom: 2px solid {border_color} !important;
        padding: 1rem !important;
    }}
    .stDataFrame tbody td {{
        color: {text_color} !important;
        border-bottom: 1px solid {border_color} !important;
        padding: 0.75rem 1rem !important;
    }}
    .stDataFrame tbody tr:hover {{
        background: {hover_bg} !important;
    }}
    /* ----- Forms ----- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        background: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }}
    /* ----- Section Headers ----- */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {text_color};
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .section-subheader {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {text_color};
        margin: 1.5rem 0 1rem 0;
    }}
    /* ----- Badges ----- */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .badge-success {{
        background: rgba(34, 197, 94, 0.1);
        color: #16A34A;
    }}
    .badge-warning {{
        background: rgba(234, 179, 8, 0.1);
        color: #CA8A04;
    }}
    .badge-info {{
        background: rgba(37, 99, 235, 0.1);
        color: #2563EB;
    }}
    /* ----- Chat Messages ----- */
    .chat-message {{
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    .chat-avatar {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }}
    .user-avatar {{
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: white;
    }}
    .assistant-avatar {{
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
    }}
    .chat-bubble {{
        background: {card_bg};
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid {border_color};
        flex: 1;
    }}
    .chat-bubble.user {{
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: white;
        border: none;
    }}
    /* ----- Theme Toggle Button ----- */
    .theme-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .theme-toggle:hover {{
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    /* ----- Animations ----- */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{
        animation: fadeIn 0.3s ease-out;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Sponsor<span>AI</span></div>', unsafe_allow_html=True)
    
    # Stats
    sponsors_df = sponsors_to_dataframe()
    students_df = students_to_dataframe()
    messages_df = messages_to_dataframe()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'''
        <div class="sidebar-stats">
            <div class="stat-label">Sponsors</div>
            <div class="stat-number">{len(sponsors_df)}</div>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div class="sidebar-stats">
            <div class="stat-label">Students</div>
            <div class="stat-number">{len(students_df)}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Navigation
    pages = ["Dashboard", "Sponsors", "Students", "Messages", "Style Library", 
             "AI Drafting", "Chat Assistant", "Reports", "Message History", "Schedule"]
    page = st.radio("Navigation", pages, label_visibility="collapsed")
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Theme toggle
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    if st.button("🌓 Toggle Theme", use_container_width=True):
        toggle_theme()

# ============================================
# MAIN CONTENT
# ============================================

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.markdown('<div class="section-header fade-in">📊 Dashboard</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-icon" style="background: rgba(37, 99, 235, 0.1); color: #2563EB;">👥</div>
                <div>
                    <div class="card-title">{len(sponsors_df)}</div>
                    <div class="card-subtitle">Total Sponsors</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-icon" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">🎓</div>
                <div>
                    <div class="card-title">{len(students_df)}</div>
                    <div class="card-subtitle">Total Students</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">💬</div>
                <div>
                    <div class="card-title">{len(messages_df)}</div>
                    <div class="card-subtitle">Messages Sent</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        pending_df = scheduled_messages_to_dataframe(status="pending")
        st.markdown(f'''
        <div class="card fade-in">
            <div class="card-header">
                <div class="card-icon" style="background: rgba(239, 68, 68, 0.1); color: #EF4444;">⏳</div>
                <div>
                    <div class="card-title">{len(pending_df)}</div>
                    <div class="card-subtitle">Pending</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Recent activity
    st.markdown('<div class="section-subheader fade-in">Recent Activity</div>', unsafe_allow_html=True)
    recent_messages = messages_to_dataframe().tail(5)
    if not recent_messages.empty:
        st.dataframe(recent_messages, use_container_width=True)
    else:
        st.info("No recent activity.")

# ---------- SPONSORS ----------
elif page == "Sponsors":
    st.markdown('<div class="section-header fade-in">👥 Sponsors</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add Sponsor"):
        with st.form("add_sponsor_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name")
                company = st.text_input("Company")
                whatsapp = st.text_input("WhatsApp")
            with col2:
                email = st.text_input("Email")
                notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Sponsor", type="primary"):
                if name:
                    add_sponsor(name, company, whatsapp, email, notes)
                    st.success("Sponsor added!")
                    st.rerun()
                else:
                    st.error("Name is required.")
    
    df = sponsors_to_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Edit/Delete options
        selected_name = st.selectbox("Select sponsor to edit/delete", df["Name"].tolist())
        if selected_name:
            sponsor_data = df[df["Name"] == selected_name].iloc
            col1, col2 = st.columns()
            with col1:
                st.subheader(f"Edit: {selected_name}")
                with st.form("edit_sponsor_form"):
                    new_company = st.text_input("Company", value=sponsor_data.get("Company", ""))
                    new_whatsapp = st.text_input("WhatsApp", value=str(sponsor_data.get("WhatsApp", "")))
                    new_email = st.text_input("Email", value=sponsor_data.get("Email", ""))
                    new_notes = st.text_area("Notes", value=sponsor_data.get("Notes", ""))
                    
                    if st.form_submit_button("Update Sponsor", type="primary"):
                        update_sponsor(selected_name, new_company, new_whatsapp, new_email, new_notes)
                        st.success("Updated!")
                        st.rerun()
            with col2:
                if st.button("🗑️ Delete Sponsor", type="primary"):
                    delete_sponsor(selected_name)
                    st.success("Deleted!")
                    st.rerun()
    else:
        st.info("No sponsors yet.")

# ---------- STUDENTS ----------
elif page == "Students":
    st.markdown('<div class="section-header fade-in">🎓 Students</div>', unsafe_allow_html=True)
    
    grades_df = get_grades()
    sponsors_df = sponsors_to_dataframe()
    
    with st.expander("➕ Add Student"):
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                student_code = st.text_input("Student Code")
                name = st.text_input("Name")
                age = st.number_input("Age", min_value=3, max_value=25, value=10)
                contact_info = st.text_input("Contact Info")
                address = st.text_input("Address")
            with col2:
                grade = st.selectbox("Grade", grades_df["name"].tolist())
                sponsor = st.selectbox("Sponsor", [None] + sponsors_df["Name"].tolist())
                auto_send = st.checkbox("Auto Send Reports", value=True)
                notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Student", type="primary"):
                if student_code and name:
                    grade_id = grades_df[grades_df["name"] == grade]["id"].values
                    sponsor_id = None
                    if sponsor:
                        sponsor_row = sponsors_df[sponsors_df["Name"] == sponsor]
                        sponsor_id = sponsor_row["id"].values if not sponsor_row.empty else None
                    
                    add_student(student_code, name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
                    st.success("Student added!")
                    st.rerun()
                else:
                    st.error("Code and Name are required.")
    
    df = students_to_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Edit/Delete
        selected_code = st.selectbox("Select student to edit/delete", df["Student Code"].tolist())
        if selected_code:
            student_data = df[df["Student Code"] == selected_code].iloc
            col1, col2 = st.columns()
            with col1:
                st.subheader(f"Edit: {student_data['Name']}")
                with st.form("edit_student_form"):
                    new_name = st.text_input("Name", value=student_data["Name"])
                    new_age = st.number_input("Age", value=int(student_data["Age"]))
                    new_contact = st.text_input("Contact Info", value=str(student_data.get("Contact Info", "")))
                    new_address = st.text_input("Address", value=str(student_data.get("Address", "")))
                    new_grade = st.selectbox("Grade", grades_df["name"].tolist(), index=grades_df[grades_df["name"] == student_data["Grade"]].index if student_data.get("Grade") in grades_df["name"].values else 0)
                    new_sponsor = st.selectbox("Sponsor", [None] + sponsors_df["Name"].tolist(), index=sponsors_df[sponsors_df["Name"] == student_data.get("Sponsor")].index+1 if student_data.get("Sponsor") in sponsors_df["Name"].values else 0)
                    new_auto = st.checkbox("Auto Send", value=bool(student_data.get("Auto Send", True)))
                    new_notes = st.text_area("Notes", value=str(student_data.get("Notes", "")))
                    
                    if st.form_submit_button("Update Student", type="primary"):
                        grade_id = grades_df[grades_df["name"] == new_grade]["id"].values
                        sponsor_id = None
                        if new_sponsor:
                            sponsor_row = sponsors_df[sponsors_df["Name"] == new_sponsor]
                            sponsor_id = sponsor_row["id"].values if not sponsor_row.empty else None
                        
                        update_student(int(student_data["ID"]), new_name, new_age, new_contact, new_address, grade_id, sponsor_id, new_auto, new_notes)
                        st.success("Updated!")
                        st.rerun()
            with col2:
                if st.button("🗑️ Delete Student", type="primary"):
                    delete_student(int(student_data["ID"]))
                    st.success("Deleted!")
                    st.rerun()
    else:
        st.info("No students yet.")

# ---------- MESSAGES ----------
elif page == "Messages":
    st.markdown('<div class="section-header fade-in">💬 Compose Message</div>', unsafe_allow_html=True)
    
    sponsors_df = sponsors_to_dataframe()
    if sponsors_df.empty:
        st.warning("No sponsors found. Add sponsors first.")
    else:
        recipient = st.selectbox("Recipient", sponsors_df["Name"].tolist())
        channel = st.selectbox("Channel", ["Email", "WhatsApp"])
        subject = st.text_input("Subject (Email only)")
        message = st.text_area("Message")
        
        col1, col2 = st.columns()
        with col1:
            send_btn = st.button("Send", type="primary")
        
        if send_btn and message:
            sponsor_data = sponsors_df[sponsors_df["Name"] == recipient].iloc
            success = False
            
            if channel == "Email":
                email = sponsor_data.get("Email")
                if email:
                    result = send_email(email, subject or "Message", message)
                    if result.get("success"):
                        add_message(str(datetime.date.today()), recipient, "Email", "Outbound", message, "Sent")
                        st.success("Email sent!")
                        success = True
                    else:
                        st.error(f"Failed: {result.get('error')}")
                else:
                    st.error("No email for this sponsor.")
            elif channel == "WhatsApp":
                phone = sponsor_data.get("WhatsApp")
                if phone:
                    result = send_whatsapp(str(phone), message)
                    if result.get("success"):
                        add_message(str(datetime.date.today()), recipient, "WhatsApp", "Outbound", message, "Sent")
                        st.success("WhatsApp sent!")
                        success = True
                    else:
                        st.error(f"Failed: {result.get('error')}")
                else:
                    st.error("No WhatsApp for this sponsor.")
            
            if success:
                st.rerun()

# ---------- STYLE LIBRARY ----------
elif page == "Style Library":
    st.markdown('<div class="section-header fade-in">📚 Style Library</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add Example"):
        with st.form("add_style_form"):
            category = st.text_input("Category")
            example = st.text_area("Example Message")
            golden = st.checkbox("Golden Example", help="Mark as reference quality")
            
            if st.form_submit_button("Add Example", type="primary"):
                if category and example:
                    add_style(category, example, golden)
                    st.success("Added!")
                    st.rerun()
                else:
                    st.error("Both fields required.")
    
    df = styles_to_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No examples yet.")

# ---------- AI DRAFTING ----------
elif page == "AI Drafting":
    st.markdown('<div class="section-header fade-in">✨ AI Message Drafting</div>', unsafe_allow_html=True)
    
    styles_df = styles_to_dataframe()
    styles_text = "\n".join(styles_df["Example"].tolist()) if not styles_df.empty else "No examples provided."
    
    uploaded_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg"])
    image_description = ""
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image_description = describe_image(image_bytes)
        st.info(f"Image described: {image_description[:100]}...")
    
    user_prompt = st.text_area("What should the message say?")
    
    if st.button("Generate Draft", type="primary") and user_prompt:
        with st.spinner("Generating..."):
            draft = generate_message(user_prompt, styles_text, image_description)
            st.success("Draft generated!")
            st.text_area("Generated Draft", draft, height=200, key="draft_output")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy to Clipboard"):
                    st.code(draft)
            with col2:
                save_draft = st.text_input("Save as draft (enter name)")
                if save_draft:
                    if "drafts" not in st.session_state:
                        st.session_state.drafts = {}
                    st.session_state.drafts[save_draft] = draft
                    st.success("Saved!")

# ---------- CHAT ASSISTANT ----------
elif page == "Chat Assistant":
    st.markdown('<div class="section-header fade-in">🤖 AI Chat Assistant</div>', unsafe_allow_html=True)
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(f'''
            <div class="chat-message fade-in">
                <div class="chat-avatar user-avatar">U</div>
                <div class="chat-bubble user">{content}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-message fade-in">
                <div class="chat-avatar assistant-avatar">AI</div>
                <div class="chat-bubble">{content}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask me anything about sponsors, students, or messaging...")
    if st.button("Send", type="primary") and user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Thinking..."):
            styles_df = styles_to_dataframe()
            styles_text = "\n".join(styles_df["Example"].tolist()) if not styles_df.empty else ""
            
            response = chat_assistant(st.session_state.chat_messages, styles_text)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    if st.button("Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

# ---------- REPORTS ----------
elif page == "Reports":
    st.markdown('<div class="section-header fade-in">📄 Student Reports</div>', unsafe_allow_html=True)
    
    students_df = students_to_dataframe()
    if students_df.empty:
        st.warning("No students found.")
    else:
        uploaded_files = st.file_uploader("Upload report files", accept_multiple_files=True, type=["pdf", "doc", "docx"])
        if uploaded_files:
            student_names = students_df["Name"].tolist()
            file_names = [f.name.rsplit(".", 1) for f in uploaded_files]
            
            with st.spinner("Matching files to students..."):
                mapping = match_files_to_students(file_names, student_names)
            
            st.subheader("File Matching Results")
            for fname, sname in mapping.items():
                status = "✅" if sname else "❌"
                st.write(f"{status} {fname} → {sname or 'Unknown'}")
            
            if st.button("Save All Matched"):
                for f, (fname, sname) in zip(uploaded_files, mapping.items()):
                    if sname:
                        student_row = students_df[students_df["Name"] == sname]
                        if not student_row.empty:
                            student_id = student_row.iloc["ID"]
                            save_path = f"data/reports/{f.name}"
                            with open(save_path, "wb") as out:
                                out.write(f.getbuffer())
                            add_report(student_id, save_path, f.name)
                st.success("Reports saved!")
                st.rerun()
    
    # View reports
    st.subheader("All Reports")
    reports_df = reports_to_dataframe()
    if not reports_df.empty:
        st.dataframe(reports_df, use_container_width=True)
    else:
        st.info("No reports uploaded yet.")

# ---------- MESSAGE HISTORY ----------
elif page == "Message History":
    st.markdown('<div class="section-header fade-in">📜 Message History</div>', unsafe_allow_html=True)
    df = messages_to_dataframe()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No messages yet.")

# ---------- SCHEDULE ----------
elif page == "Schedule":
    st.markdown('<div class="section-header fade-in">⏳ Scheduled Messages</div>', unsafe_allow_html=True)
    
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
            if st.form_submit_button("Schedule", type="primary"):
                if recipient != "Select..." and message:
                    add_scheduled_message(recipient, channel, message, send_dt.isoformat())
                    st.success("Scheduled!")
                    st.rerun()
    
    st.subheader("📋 Pending")
    pending_df = scheduled_messages_to_dataframe(status="pending")
    if not pending_df.empty:
        for _, row in pending_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns()
                col1.write(f"**{row['Recipient']}** – {row['Message'][:60]}...")
                col1.caption(f"📅 {row['Send Time']}")
                with col2:
                    if st.button("Send Now", key=f"send_{row['ID']}"):
                        sponsor = sponsors_df[sponsors_df["Name"] == row["Recipient"]].iloc
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
