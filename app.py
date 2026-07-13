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
    reports_to_dataframe,
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
import html

BRAND_ICON = "✦"
EMPTY_DISPLAY = "—"
MAX_ACTIVITY_MESSAGE_LENGTH = 96
MAX_STYLE_MESSAGE_LENGTH = 88

# Ensure data folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)

initialize_database()

st.set_page_config(
    page_title="HOPe",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# GLOBAL CSS — HOPe Dark Purple Theme
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --hope-bg: #0B0B1A;
        --hope-panel: rgba(255,255,255,0.04);
        --hope-panel-strong: rgba(255,255,255,0.06);
        --hope-border: rgba(139,92,246,0.18);
        --hope-border-strong: rgba(139,92,246,0.3);
        --hope-accent: #7C3AED;
        --hope-accent-soft: #C4B5FD;
        --hope-text: #F1F5F9;
        --hope-muted: #94A3B8;
    }

    /* ─── Reset & Base ─── */
    *, *::before, *::after { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

    .stApp {
        background: radial-gradient(ellipse 120% 80% at 50% -10%, #2d0a6e22 0%, #0B0B1A 60%) !important;
        background-color: #0B0B1A !important;
        color: #F1F5F9 !important;
    }
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1280px !important;
    }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #100820 0%, #0D0D22 100%) !important;
        border-right: 1px solid rgba(139,92,246,0.18) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem !important;
    }
    /* Sidebar radio buttons — nav items */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        display: flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
        padding: 0.55rem 0.9rem !important;
        border-radius: 8px !important;
        color: #94A3B8 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        margin: 1px 0 !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(139,92,246,0.12) !important;
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
        background: rgba(139,92,246,0.22) !important;
        color: #C4B5FD !important;
        font-weight: 600 !important;
    }
    /* Hide the radio circle */
    [data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] { display: none !important; }

    /* ─── Cards ─── */
    .hope-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.25rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .hope-card:hover {
        border-color: rgba(139,92,246,0.38);
        box-shadow: 0 0 20px rgba(139,92,246,0.08);
    }

    /* ─── Stat Cards ─── */
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        border-color: rgba(139,92,246,0.4);
        box-shadow: 0 0 24px rgba(139,92,246,0.1);
    }
    .stat-card .stat-icon {
        font-size: 1.4rem;
        margin-bottom: 0.2rem;
    }
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #F1F5F9;
        line-height: 1;
    }
    .stat-card .stat-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    /* ─── Page Headings ─── */
    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #F1F5F9;
        margin-bottom: 0.35rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .page-title span.accent { color: #A78BFA; }
    .page-subtitle {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.75rem;
    }
    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #4B5563;
        padding: 0.6rem 0.9rem 0.3rem;
        margin-top: 0.5rem;
    }

    /* ─── Buttons ─── */
    .stButton > button {
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        transition: all 0.18s ease !important;
        border: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
        color: #fff !important;
        box-shadow: 0 2px 12px rgba(124,58,237,0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
        box-shadow: 0 4px 18px rgba(124,58,237,0.5) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.06) !important;
        color: #C4B5FD !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(139,92,246,0.15) !important;
    }

    /* ─── Inputs / Forms ─── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(139,92,246,0.2) !important;
        border-radius: 9px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stNumberInput label, .stFileUploader label, .stCheckbox label {
        color: #94A3B8 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    .stCheckbox > div > div { color: #94A3B8 !important; }

    /* ─── Tables / DataFrames ─── */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(139,92,246,0.18) !important;
    }
    .stDataFrame thead th {
        background: rgba(124,58,237,0.12) !important;
        color: #C4B5FD !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        border-bottom: 1px solid rgba(139,92,246,0.25) !important;
    }
    .stDataFrame tbody td {
        color: #CBD5E1 !important;
        border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        font-size: 0.88rem !important;
    }
    .stDataFrame tbody tr:hover td {
        background: rgba(139,92,246,0.07) !important;
    }

    /* ─── Expanders ─── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(139,92,246,0.18) !important;
        border-radius: 10px !important;
        color: #C4B5FD !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(139,92,246,0.12) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
    }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        padding: 3px !important;
        gap: 2px !important;
        border: 1px solid rgba(139,92,246,0.18) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px !important;
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.4rem 1.2rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(124,58,237,0.35) !important;
        color: #C4B5FD !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* ─── Info / Warning / Success alerts ─── */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid rgba(139,92,246,0.25) !important;
        background: rgba(124,58,237,0.08) !important;
    }

    /* ─── Badges ─── */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-success { background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.25); }
    .badge-warning { background: rgba(245,158,11,0.15); color: #FCD34D; border: 1px solid rgba(245,158,11,0.25); }
    .badge-purple  { background: rgba(139,92,246,0.15); color: #C4B5FD; border: 1px solid rgba(139,92,246,0.25); }
    .badge-danger  { background: rgba(239,68,68,0.15);  color: #FCA5A5; border: 1px solid rgba(239,68,68,0.25); }

    /* ─── Table container ─── */
    .table-container {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 14px;
        overflow: hidden;
    }
    .table-header-row {
        display: grid;
        background: rgba(124,58,237,0.1);
        border-bottom: 1px solid rgba(139,92,246,0.2);
        padding: 0.65rem 1.2rem;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #7C3AED;
    }
    .table-row {
        display: grid;
        padding: 0.75rem 1.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        font-size: 0.875rem;
        color: #CBD5E1;
        align-items: center;
    }
    .table-row:last-child { border-bottom: none; }
    .table-row:hover { background: rgba(139,92,246,0.06); }

    /* ─── Chat ─── */
    .chat-msg {
        display: flex;
        gap: 0.85rem;
        margin-bottom: 0.85rem;
        animation: fadeUp 0.25s ease;
    }
    .chat-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .chat-avatar.user   { background: linear-gradient(135deg,#7C3AED,#5B21B6); color:#fff; }
    .chat-avatar.ai     { background: linear-gradient(135deg,#0EA5E9,#0284C7); color:#fff; }
    .chat-bubble {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: #E2E8F0;
        font-size: 0.9rem;
        line-height: 1.55;
        flex: 1;
    }
    .chat-bubble.user {
        background: rgba(124,58,237,0.18);
        border-color: rgba(139,92,246,0.35);
    }

    /* ─── Sidebar logo ─── */
    .hope-logo {
        font-size: 1.6rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: #F1F5F9;
        padding: 0.25rem 0.9rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .hope-logo .accent { color: #A78BFA; }
    .hope-logo .dot    { color: #7C3AED; font-size:1.8rem; }
    .sidebar-brand-icon {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(124,58,237,0.22);
        border: 1px solid rgba(139,92,246,0.35);
        box-shadow: 0 0 16px rgba(124,58,237,0.22);
    }

    /* ─── Dividers ─── */
    .sidebar-divider {
        height: 1px;
        background: rgba(139,92,246,0.15);
        margin: 0.75rem 0.9rem;
    }
    .sidebar-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #4B5563;
        padding: 0.3rem 0.9rem 0.2rem;
    }

    /* ─── Activity rows ─── */
    .activity-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.7rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .activity-row:last-child { border-bottom: none; }
    .activity-name { font-size: 0.9rem; font-weight: 600; color: #E2E8F0; }
    .activity-meta { font-size: 0.78rem; color: #64748B; margin-top: 2px; }
    .activity-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .activity-avatar {
        width: 34px;
        height: 34px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(124,58,237,0.25);
        border: 1px solid rgba(139,92,246,0.35);
        color: #DDD6FE;
        font-size: 0.8rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    .activity-excerpt {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 1px;
        max-width: 520px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .table-search-row {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.8rem 1.2rem;
        border-bottom: 1px solid rgba(139,92,246,0.16);
        color: #94A3B8;
        font-size: 0.8rem;
    }
    .ref-style-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 10px;
        padding: 0.65rem 0.75rem;
        margin-bottom: 0.5rem;
    }
    .ref-style-title {
        color: #DDD6FE;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }
    .ref-style-text {
        color: #94A3B8;
        font-size: 0.8rem;
        line-height: 1.4;
    }

    button:focus-visible, input:focus-visible, textarea:focus-visible {
        outline: 2px solid rgba(167,139,250,0.65) !important;
        outline-offset: 1px !important;
    }

    /* ─── Animations ─── */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeUp 0.3s ease; }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.3); border-radius: 3px; }

    /* ─── Divider ─── */
    hr { border-color: rgba(139,92,246,0.18) !important; }

    /* Subheaders */
    .section-subheader {
        font-size: 1rem;
        font-weight: 700;
        color: #E2E8F0;
        margin: 1.25rem 0 0.75rem;
        letter-spacing: -0.01em;
    }

    /* Search bar styling */
    .search-wrap .stTextInput > div > div > input {
        border-radius: 9px !important;
        padding-left: 2.2rem !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px dashed rgba(139,92,246,0.3) !important;
        border-radius: 12px !important;
    }

    /* Spinner color */
    .stSpinner > div { border-top-color: #7C3AED !important; }

    /* Selectbox arrow */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(139,92,246,0.2) !important;
        border-radius: 9px !important;
    }
    .stSelectbox [data-baseweb="select"] span { color: #E2E8F0 !important; }
</style>
""", unsafe_allow_html=True)


def safe_text(value):
    """Return UI-safe text by normalizing empty values and escaping HTML."""
    if value is None:
        return html.escape(EMPTY_DISPLAY)
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return html.escape(EMPTY_DISPLAY)
    return html.escape(text)


def render_table_container(df, columns, headers, row_label, search_text, grid_template=None):
    """Render a reusable dark table container with search context and rows."""
    st.markdown('<div class="table-container fade-in">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-search-row"><span>{len(df)} {row_label} found</span><span>Search: {safe_text(search_text) if search_text else "All"}</span></div>',
        unsafe_allow_html=True
    )
    grid = grid_template or " ".join(["1fr"] * max(len(headers), 1))
    st.markdown(
        f'<div class="table-header-row" style="grid-template-columns:{grid};">' +
        "".join(f"<div>{safe_text(h)}</div>" for h in headers) +
        '</div>',
        unsafe_allow_html=True
    )
    for row in df[columns].to_dict("records"):
        st.markdown(
            f'<div class="table-row" style="grid-template-columns:{grid};">' +
            "".join(f"<div>{safe_text(row.get(col, EMPTY_DISPLAY))}</div>" for col in columns) +
            '</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)


def merge_contact_info(df, primary_col, fallback_col):
    """Build a display contact field by preferring a primary column over fallback."""
    primary = df[primary_col] if primary_col in df.columns else pd.Series("", index=df.index)
    fallback = df[fallback_col] if fallback_col in df.columns else pd.Series("", index=df.index)
    return primary.replace("", pd.NA).fillna(fallback.replace("", pd.NA)).fillna(EMPTY_DISPLAY)


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    # Logo
    st.markdown(f'''
    <div class="hope-logo">
        <span class="sidebar-brand-icon">{BRAND_ICON}</span>
        <span class="accent">HOP</span><span>e</span>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Live stats mini-strip
    sponsors_df = sponsors_to_dataframe()
    students_df = get_students()
    messages_df = messages_to_dataframe()

    st.markdown(f'''
    <div style="display:flex;gap:0.6rem;padding:0 0.5rem 0.75rem;">
        <div style="flex:1;background:rgba(124,58,237,0.12);border:1px solid rgba(139,92,246,0.22);
                    border-radius:10px;padding:0.55rem 0.7rem;">
            <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748B;">Sponsors</div>
            <div style="font-size:1.4rem;font-weight:800;color:#C4B5FD;">{len(sponsors_df)}</div>
        </div>
        <div style="flex:1;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.18);
                    border-radius:10px;padding:0.55rem 0.7rem;">
            <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748B;">Students</div>
            <div style="font-size:1.4rem;font-weight:800;color:#6EE7B7;">{len(students_df)}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ── CORE section ──
    st.markdown('<div class="sidebar-section-label">CORE</div>', unsafe_allow_html=True)
    core_pages = ["Dashboard", "Sponsors", "Students", "Messages", "Reports", "Schedule"]

    # Use session_state to track which section is active
    if "active_section" not in st.session_state:
        st.session_state.active_section = "core"

    core_icon_map = {
        "Dashboard": "📊",
        "Sponsors": "👥",
        "Students": "🎓",
        "Messages": "✉️",
        "Reports": "📁",
        "Schedule": "🗓️",
    }

    core_sel = st.radio(
        "core_nav",
        core_pages,
        label_visibility="collapsed",
        key="core_radio",
        format_func=lambda p: f"{core_icon_map.get(p, '•')}  {p}",
    )

    st.markdown('<div style="margin-top:0.5rem"></div>', unsafe_allow_html=True)

    # ── INTELLIGENCE section ──
    st.markdown('<div class="sidebar-section-label">INTELLIGENCE</div>', unsafe_allow_html=True)
    intel_pages = ["AI Intelligence", "Style Library", "Message History"]

    intel_icon_map = {
        "AI Intelligence": "🧠",
        "Style Library": "🎨",
        "Message History": "🕘",
    }

    intel_sel = st.radio(
        "intel_nav",
        intel_pages,
        label_visibility="collapsed",
        key="intel_radio",
        format_func=lambda p: f"{intel_icon_map.get(p, '•')}  {p}",
    )

    # Determine active page: whichever radio was last interacted with
    # We track this by comparing against stored values
    if "prev_core" not in st.session_state:
        st.session_state.prev_core = core_sel
    if "prev_intel" not in st.session_state:
        st.session_state.prev_intel = intel_sel

    if core_sel != st.session_state.prev_core:
        st.session_state.active_section = "core"
        st.session_state.prev_core = core_sel
    elif intel_sel != st.session_state.prev_intel:
        st.session_state.active_section = "intel"
        st.session_state.prev_intel = intel_sel

    page = core_sel if st.session_state.active_section == "core" else intel_sel

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('''
    <div style="padding:0.3rem 0.9rem;font-size:0.78rem;color:#4B5563;">
        HOPe Sponsor Assistant
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('<div style="padding-top:0.4rem"></div>', unsafe_allow_html=True)
    if st.button("↩ Logout", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ============================================
# DASHBOARD
# ============================================
if page == "Dashboard":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">Welcome to <span class="accent">HOPe</span></div>
        <div class="page-subtitle">Your sponsor relationship & student support dashboard</div>
    </div>
    ''', unsafe_allow_html=True)

    # ── Stats row ──
    pending_df = scheduled_messages_to_dataframe(status="pending")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'''
        <div class="stat-card fade-in">
            <div class="stat-icon">👥</div>
            <div class="stat-value">{len(sponsors_df)}</div>
            <div class="stat-label">Total Sponsors</div>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div class="stat-card fade-in">
            <div class="stat-icon">🎓</div>
            <div class="stat-value">{len(students_df)}</div>
            <div class="stat-label">Students Supported</div>
        </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
        <div class="stat-card fade-in">
            <div class="stat-icon">💬</div>
            <div class="stat-value">{len(messages_df)}</div>
            <div class="stat-label">Messages Sent</div>
        </div>
        ''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''
        <div class="stat-card fade-in">
            <div class="stat-icon">⏳</div>
            <div class="stat-value">{len(pending_df)}</div>
            <div class="stat-label">Pending Action</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1.75rem"></div>', unsafe_allow_html=True)

    # ── Recent Activity ──
    st.markdown('<div class="section-subheader">Recent Activity</div>', unsafe_allow_html=True)
    recent_messages = messages_to_dataframe().tail(8)

    if not recent_messages.empty:
        st.markdown('<div class="hope-card">', unsafe_allow_html=True)
        for _, row in recent_messages.iterrows():
            channel = str(row.get("Channel", ""))
            status  = str(row.get("Status", ""))
            badge_cls = "badge-success" if status.lower() == "sent" else "badge-warning"
            ch_badge  = "badge-purple" if "email" in channel.lower() else "badge-warning"
            recipient_raw = str(row.get("Recipient", "") or "").strip()
            recipient = safe_text(recipient_raw or "—")
            date_txt = safe_text(row.get("Date", ""))
            msg_raw = str(row.get("Message", "") or "").strip()
            msg_excerpt = safe_text(
                (msg_raw[:MAX_ACTIVITY_MESSAGE_LENGTH] + "…")
                if len(msg_raw) > MAX_ACTIVITY_MESSAGE_LENGTH
                else (msg_raw or "No message body")
            )
            avatar = safe_text(recipient_raw[:1].upper() if recipient_raw else "?")

            st.markdown(f'''
            <div class="activity-row">
                <div class="activity-left">
                    <div class="activity-avatar">{avatar}</div>
                    <div>
                        <div class="activity-name">{recipient}</div>
                        <div class="activity-excerpt">{msg_excerpt}</div>
                        <div class="activity-meta">{date_txt}</div>
                    </div>
                </div>
                <div style="display:flex;gap:0.5rem;align-items:center;">
                    <span class="badge {ch_badge}">{safe_text(channel)}</span>
                    <span class="badge {badge_cls}">{safe_text(status)}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2.5rem 1.5rem;">
            <div style="font-size:2rem;margin-bottom:0.75rem;">📭</div>
            <div style="color:#64748B;font-size:0.9rem;">No recent activity yet. Start by adding a sponsor!</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================
# SPONSORS
# ============================================
elif page == "Sponsors":
    # Header row with action button
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown('''
        <div class="fade-in">
            <div class="page-title">Sponsors</div>
            <div class="page-subtitle">Manage and track all your sponsor relationships</div>
        </div>
        ''', unsafe_allow_html=True)
    with hcol2:
        st.markdown('<div style="padding-top:1.5rem"></div>', unsafe_allow_html=True)
        show_add = st.button("➕ Add Sponsor", type="primary", use_container_width=True)

    # Search
    search_col, _ = st.columns([2, 3])
    with search_col:
        search_q = st.text_input("Search sponsors", key="sponsor_search", label_visibility="visible",
                                 placeholder="Search by name or company…")

    # Add sponsor form
    if show_add or st.session_state.get("show_add_sponsor_form"):
        st.session_state["show_add_sponsor_form"] = True
        st.markdown('<div class="hope-card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-subheader" style="margin-top:0">Add New Sponsor</div>', unsafe_allow_html=True)
        with st.form("add_sponsor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name    = st.text_input("Full Name *")
                company = st.text_input("Company / Organisation")
                whatsapp = st.text_input("WhatsApp Number")
            with col2:
                email = st.text_input("Email Address")
                notes = st.text_area("Notes", height=118)
            fc1, fc2 = st.columns([1, 5])
            with fc1:
                submitted = st.form_submit_button("Add Sponsor", type="primary")
            with fc2:
                if st.form_submit_button("Cancel", type="secondary"):
                    st.session_state["show_add_sponsor_form"] = False
                    st.rerun()
            if submitted:
                if name:
                    add_sponsor(name, company, whatsapp, email, notes)
                    st.success("✅ Sponsor added successfully!")
                    st.session_state["show_add_sponsor_form"] = False
                    st.rerun()
                else:
                    st.error("Name is required.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Sponsor table
    df = sponsors_to_dataframe()
    if search_q:
        mask = df.apply(lambda r: search_q.lower() in str(r).lower(), axis=1)
        df = df[mask]

    if not df.empty:
        sponsors_view = df.copy()
        sponsors_view["Sponsor"] = sponsors_view.get("Name", "")
        sponsors_view["Contact"] = merge_contact_info(sponsors_view, "Email", "WhatsApp")
        sponsors_view["Notes"] = sponsors_view.get("Notes", "")
        sponsors_view["Actions"] = "Manage below"
        render_table_container(
            sponsors_view,
            columns=["Sponsor", "Contact", "Notes", "Actions"],
            headers=["Sponsor", "Contact", "Notes", "Actions"],
            row_label=f'sponsor{"s" if len(df) != 1 else ""}',
            search_text=search_q,
            grid_template="1.2fr 1fr 1.2fr 0.8fr"
        )

        st.markdown('<div class="section-subheader">Edit or Remove Sponsor</div>', unsafe_allow_html=True)
        selected_name = st.selectbox("Select sponsor", df["Name"].tolist(), key="sel_sponsor")
        if selected_name:
            sponsor_data = df[df["Name"] == selected_name].iloc[0]
            edit_col, del_col = st.columns([3, 1])
            with edit_col:
                st.markdown('<div class="hope-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="section-subheader" style="margin-top:0">Editing: {selected_name}</div>', unsafe_allow_html=True)
                with st.form("edit_sponsor_form"):
                    new_company  = st.text_input("Company", value=sponsor_data.get("Company", ""))
                    new_whatsapp = st.text_input("WhatsApp", value=str(sponsor_data.get("WhatsApp", "")))
                    new_email    = st.text_input("Email", value=sponsor_data.get("Email", ""))
                    new_notes    = st.text_area("Notes", value=sponsor_data.get("Notes", ""))
                    if st.form_submit_button("Update Sponsor", type="primary"):
                        update_sponsor(selected_name, new_company, new_whatsapp, new_email, new_notes)
                        st.success("✅ Updated!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with del_col:
                st.markdown('<div style="padding-top:3.25rem"></div>', unsafe_allow_html=True)
                if st.button("🗑️ Delete Sponsor", use_container_width=True):
                    delete_sponsor(selected_name)
                    st.success("Deleted!")
                    st.rerun()
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:3rem 1.5rem;">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">👥</div>
            <div style="color:#E2E8F0;font-weight:600;margin-bottom:0.4rem;">No sponsors yet</div>
            <div style="color:#64748B;font-size:0.88rem;">Click "Add Sponsor" to get started.</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================
# STUDENTS
# ============================================
elif page == "Students":
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown('''
        <div class="fade-in">
            <div class="page-title">Students</div>
            <div class="page-subtitle">Track students and their sponsor assignments</div>
        </div>
        ''', unsafe_allow_html=True)
    with hcol2:
        st.markdown('<div style="padding-top:1.5rem"></div>', unsafe_allow_html=True)
        show_add_student = st.button("➕ Add Student", type="primary", use_container_width=True)

    # Search
    search_col, _ = st.columns([2, 3])
    with search_col:
        student_search = st.text_input("Search students", key="student_search", label_visibility="visible",
                                       placeholder="Search students…")

    grades_df   = get_grades()
    sponsors_df = sponsors_to_dataframe()

    # Add student form
    if show_add_student or st.session_state.get("show_add_student_form"):
        st.session_state["show_add_student_form"] = True
        st.markdown('<div class="hope-card fade-in">', unsafe_allow_html=True)
        st.markdown('<div class="section-subheader" style="margin-top:0">Add New Student</div>', unsafe_allow_html=True)
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                student_code = st.text_input("Student Code *")
                name         = st.text_input("Full Name *")
                age          = st.number_input("Age", min_value=3, max_value=25, value=10)
                contact_info = st.text_input("Contact Info")
                address      = st.text_input("Address")
            with col2:
                grade   = st.selectbox("Grade", grades_df["name"].tolist())
                sponsor = st.selectbox("Sponsor", [None] + sponsors_df["Name"].tolist())
                auto_send = st.checkbox("Auto Send Reports", value=True)
                notes   = st.text_area("Notes", height=100)

            fc1, fc2 = st.columns([1, 5])
            with fc1:
                submitted = st.form_submit_button("Add Student", type="primary")
            with fc2:
                if st.form_submit_button("Cancel", type="secondary"):
                    st.session_state["show_add_student_form"] = False
                    st.rerun()

            if submitted:
                if student_code and name:
                    grade_id = grades_df[grades_df["name"] == grade]["id"].iloc[0]
                    sponsor_id = None
                    if sponsor:
                        sponsor_row = sponsors_df[sponsors_df["Name"] == sponsor]
                        sponsor_id = sponsor_row["ID"].iloc[0] if not sponsor_row.empty else None
                    add_student(name, age, contact_info, address, grade_id, sponsor_id, auto_send, notes)
                    st.success("✅ Student added!")
                    st.session_state["show_add_student_form"] = False
                    st.rerun()
                else:
                    st.error("Code and Name are required.")
        st.markdown('</div>', unsafe_allow_html=True)

    df = get_students()
    if student_search:
        mask = df.apply(lambda r: student_search.lower() in str(r).lower(), axis=1)
        df = df[mask]

    if not df.empty:
        students_view = df.copy()
        students_view["Student"] = students_view.get("name", "")
        students_view["Contact"] = students_view.get("contact_info", "")
        students_view["Notes"] = students_view.get("notes", "")
        students_view["Actions"] = "Manage below"
        render_table_container(
            students_view,
            columns=["Student", "Contact", "Notes", "Actions"],
            headers=["Student", "Contact", "Notes", "Actions"],
            row_label=f'student{"s" if len(df) != 1 else ""}',
            search_text=student_search,
            grid_template="1.2fr 1fr 1.2fr 0.8fr"
        )

        st.markdown('<div class="section-subheader">Edit or Remove Student</div>', unsafe_allow_html=True)
        selected_code = st.selectbox("Select student", df["student_code"].tolist(), key="sel_student")
        if selected_code:
            student_data = df[df["student_code"] == selected_code].iloc[0]
            edit_col, del_col = st.columns([3, 1])
            with edit_col:
                st.markdown('<div class="hope-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="section-subheader" style="margin-top:0">Editing: {student_data["name"]}</div>', unsafe_allow_html=True)
                with st.form("edit_student_form"):
                    new_name    = st.text_input("Name", value=student_data["name"])
                    new_age     = st.number_input("Age", value=int(student_data["age"]))
                    new_contact = st.text_input("Contact Info", value=str(student_data.get("contact_info", "")))
                    new_address = st.text_input("Address", value=str(student_data.get("address", "")))
                    grade_idx   = grades_df[grades_df["name"] == student_data["grade_name"]].index[0] if student_data["grade_name"] in grades_df["name"].values else 0
                    new_grade   = st.selectbox("Grade", grades_df["name"].tolist(), index=int(grade_idx))
                    sp_idx      = sponsors_df[sponsors_df["Name"] == student_data["sponsor_name"]].index[0] + 1 if student_data.get("sponsor_name") in sponsors_df["Name"].values else 0
                    new_sponsor = st.selectbox("Sponsor", [None] + sponsors_df["Name"].tolist(), index=int(sp_idx))
                    new_auto    = st.checkbox("Auto Send", value=bool(student_data.get("auto_send", True)))
                    new_notes   = st.text_area("Notes", value=str(student_data.get("notes", "")))
                    if st.form_submit_button("Update Student", type="primary"):
                        grade_id = grades_df[grades_df["name"] == new_grade]["id"].iloc[0]
                        sponsor_id = None
                        if new_sponsor:
                            sponsor_row = sponsors_df[sponsors_df["Name"] == new_sponsor]
                            sponsor_id = sponsor_row["ID"].iloc[0] if not sponsor_row.empty else None
                        update_student(int(student_data["id"]), new_name, new_age, new_contact, new_address, grade_id, sponsor_id, new_auto, new_notes)
                        st.success("✅ Updated!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with del_col:
                st.markdown('<div style="padding-top:3.25rem"></div>', unsafe_allow_html=True)
                if st.button("🗑️ Delete Student", use_container_width=True):
                    delete_student(int(student_data["id"]))
                    st.success("Deleted!")
                    st.rerun()
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:3rem 1.5rem;">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">🎓</div>
            <div style="color:#E2E8F0;font-weight:600;margin-bottom:0.4rem;">No students yet</div>
            <div style="color:#64748B;font-size:0.88rem;">Click "Add Student" to begin tracking students.</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================
# MESSAGES
# ============================================
elif page == "Messages":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">Compose <span class="accent">Message</span></div>
        <div class="page-subtitle">Send emails or WhatsApp messages directly to sponsors</div>
    </div>
    ''', unsafe_allow_html=True)

    sponsors_df = sponsors_to_dataframe()
    if sponsors_df.empty:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2.5rem;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">⚠️</div>
            <div style="color:#FCD34D;">No sponsors found. Add sponsors first.</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hope-card">', unsafe_allow_html=True)
        recipient = st.selectbox("Recipient", sponsors_df["Name"].tolist())
        channel   = st.selectbox("Channel", ["Email", "WhatsApp"])
        subject   = st.text_input("Subject (Email only)")
        message   = st.text_area("Message", height=140)
        send_btn  = st.button("📤 Send Message", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        if send_btn and message:
            sponsor_data = sponsors_df[sponsors_df["Name"] == recipient].iloc[0]
            success = False
            if channel == "Email":
                email_addr = sponsor_data.get("Email")
                if email_addr:
                    result = send_email(email_addr, subject or "Message", message)
                    if result.get("success"):
                        add_message(str(datetime.date.today()), recipient, "Email", "Outbound", message, "Sent")
                        st.success("✅ Email sent!")
                        success = True
                    else:
                        st.error(f"Failed: {result.get('error')}")
                else:
                    st.error("No email address for this sponsor.")
            elif channel == "WhatsApp":
                phone = sponsor_data.get("WhatsApp")
                if phone:
                    result = send_whatsapp(str(phone), message)
                    if result.get("success"):
                        add_message(str(datetime.date.today()), recipient, "WhatsApp", "Outbound", message, "Sent")
                        st.success("✅ WhatsApp sent!")
                        success = True
                    else:
                        st.error(f"Failed: {result.get('error')}")
                else:
                    st.error("No WhatsApp number for this sponsor.")
            if success:
                st.rerun()


# ============================================
# AI INTELLIGENCE (Drafting + Chat)
# ============================================
elif page == "AI Intelligence":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">AI Intelligence</div>
        <div class="page-subtitle">Generate sponsor messages and get AI-powered assistance</div>
    </div>
    ''', unsafe_allow_html=True)

    tab_draft, tab_chat = st.tabs(["✍️  Draft Message", "💬  Chat Assistant"])

    # ─── Draft tab ───
    with tab_draft:
        left_col, right_col = st.columns([5, 4], gap="large")

        with left_col:
            st.markdown('<div class="section-subheader">Message Prompt</div>', unsafe_allow_html=True)
            user_prompt = st.text_area(
                "What should the message say?",
                height=160,
                placeholder="e.g. Write a warm update for our sponsor thanking them for their contribution this month…",
                label_visibility="collapsed"
            )

            uploaded_file = st.file_uploader("Attach image (optional)", type=["png", "jpg", "jpeg"])

            # Style reference chips
            styles_df = styles_to_dataframe()
            if not styles_df.empty:
                st.markdown('<div class="section-subheader" style="margin-top:1rem">Reference Styles (Optional)</div>', unsafe_allow_html=True)
                for _, srow in styles_df.head(6).iterrows():
                    cat = safe_text(srow.get("Category", ""))
                    gold = "⭐ " if srow.get("Golden") else ""
                    msg = str(srow.get("Message", "") or "").strip()
                    msg_excerpt = safe_text(
                        (msg[:MAX_STYLE_MESSAGE_LENGTH] + "…")
                        if len(msg) > MAX_STYLE_MESSAGE_LENGTH
                        else (msg or "Style example")
                    )
                    st.markdown(
                        f'<div class="ref-style-card"><div class="ref-style-title">{gold}{cat}</div><div class="ref-style-text">{msg_excerpt}</div></div>',
                        unsafe_allow_html=True
                    )

            gen_btn = st.button("✨ Generate Draft", type="primary", use_container_width=True)

        with right_col:
            st.markdown('<div class="section-subheader">Generated Output</div>', unsafe_allow_html=True)

            if gen_btn and user_prompt:
                with st.spinner("Generating draft…"):
                    image_description = ""
                    if uploaded_file:
                        image_bytes = uploaded_file.read()
                        image_description = describe_image(image_bytes)

                    styles_text = "\n".join(styles_df["Message"].tolist()) if not styles_df.empty else "No examples provided."
                    draft = generate_message(user_prompt, styles_text, image_description)
                    st.session_state["last_draft"] = draft
                    st.success("Draft ready!")

            if "last_draft" in st.session_state:
                st.markdown('<div class="hope-card">', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#E2E8F0;line-height:1.6;white-space:pre-wrap;font-size:0.9rem">{st.session_state["last_draft"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if st.button("📋 Copy Text", type="secondary", use_container_width=True):
                    st.code(st.session_state["last_draft"], language=None)
            else:
                st.markdown('''
                <div class="hope-card" style="text-align:center;padding:3rem 1rem;min-height:200px;
                     display:flex;flex-direction:column;align-items:center;justify-content:center;">
                    <div style="font-size:2rem;margin-bottom:0.5rem;">✨</div>
                    <div style="color:#64748B;font-size:0.875rem;">Your generated draft will appear here</div>
                </div>
                ''', unsafe_allow_html=True)

    # ─── Chat tab ───
    with tab_chat:
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        # Chat history
        if st.session_state.chat_messages:
            for msg in st.session_state.chat_messages:
                role    = msg["role"]
                content = msg["content"]
                if role == "user":
                    st.markdown(f'''
                    <div class="chat-msg fade-in">
                        <div class="chat-avatar user">U</div>
                        <div class="chat-bubble user">{content}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="chat-msg fade-in">
                        <div class="chat-avatar ai">AI</div>
                        <div class="chat-bubble">{content}</div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="hope-card" style="text-align:center;padding:2rem;margin-bottom:1rem;">
                <div style="font-size:1.8rem;margin-bottom:0.5rem;">🤖</div>
                <div style="color:#94A3B8;font-size:0.875rem;">
                    Ask me anything about your sponsors, students, or request a message draft.
                </div>
            </div>
            ''', unsafe_allow_html=True)

        user_input = st.text_input(
            "Message",
            key="chat_input",
            label_visibility="collapsed",
            placeholder="Ask me anything about sponsors, students, or messaging…"
        )
        chat_col1, chat_col2 = st.columns([1, 1])
        with chat_col1:
            if st.button("Send", type="primary", use_container_width=True) and user_input:
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                with st.spinner("Thinking…"):
                    styles_df_c = styles_to_dataframe()
                    styles_text = "\n".join(styles_df_c["Message"].tolist()) if not styles_df_c.empty else ""
                    response = chat_assistant(st.session_state.chat_messages, styles_text)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
        with chat_col2:
            if st.button("Clear Chat", type="secondary", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()


# ============================================
# STYLE LIBRARY
# ============================================
elif page == "Style Library":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">Style <span class="accent">Library</span></div>
        <div class="page-subtitle">Manage writing style examples used by AI to match your voice</div>
    </div>
    ''', unsafe_allow_html=True)

    with st.expander("➕ Add Style Example"):
        with st.form("add_style_form", clear_on_submit=True):
            category = st.text_input("Category")
            example  = st.text_area("Example Message", height=120)
            golden   = st.checkbox("⭐ Golden Example", help="Mark as reference quality")
            if st.form_submit_button("Add Example", type="primary"):
                if category and example:
                    add_style(category, example, golden)
                    st.success("✅ Added!")
                    st.rerun()
                else:
                    st.error("Both fields required.")

    df = styles_to_dataframe()
    if not df.empty:
        st.markdown('<div class="hope-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2.5rem;">
            <div style="color:#64748B;">No style examples yet. Add some to improve AI quality.</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================
# REPORTS
# ============================================
elif page == "Reports":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">Student <span class="accent">Reports</span></div>
        <div class="page-subtitle">Upload and manage student progress reports</div>
    </div>
    ''', unsafe_allow_html=True)

    students_df = get_students()
    if students_df.empty:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2.5rem;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">⚠️</div>
            <div style="color:#FCD34D;">No students found. Add students first.</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        uploaded_files = st.file_uploader(
            "Upload report files",
            accept_multiple_files=True,
            type=["pdf", "doc", "docx"]
        )
        if uploaded_files:
            student_names = students_df["name"].tolist()
            file_names    = [f.name for f in uploaded_files]
            with st.spinner("Matching files to students…"):
                base_names = [f.rsplit(".", 1)[0] for f in file_names]
                mapping    = match_files_to_students(base_names, student_names)

            st.markdown('<div class="section-subheader">File Matching Results</div>', unsafe_allow_html=True)
            st.markdown('<div class="hope-card">', unsafe_allow_html=True)
            for f, (base, sname) in zip(uploaded_files, mapping.items()):
                badge = '<span class="badge badge-success">✓ Matched</span>' if sname else '<span class="badge badge-danger">✗ Unknown</span>'
                st.markdown(f'''
                <div class="activity-row">
                    <div class="activity-name">{f.name}</div>
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                        <span style="color:#94A3B8;font-size:0.85rem;">{sname or "—"}</span>
                        {badge}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("💾 Save All Matched", type="primary"):
                for f, (base, sname) in zip(uploaded_files, mapping.items()):
                    if sname:
                        student_row = students_df[students_df["name"] == sname]
                        if not student_row.empty:
                            student_id = student_row.iloc[0]["id"]
                            save_path  = f"data/reports/{f.name}"
                            with open(save_path, "wb") as out:
                                out.write(f.getbuffer())
                            add_report(student_id, save_path, f.name)
                st.success("✅ Reports saved!")
                st.rerun()

    st.markdown('<div class="section-subheader">All Reports</div>', unsafe_allow_html=True)
    reports_df = reports_to_dataframe()
    if not reports_df.empty:
        st.markdown('<div class="hope-card">', unsafe_allow_html=True)
        st.dataframe(reports_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2rem;">
            <div style="color:#64748B;font-size:0.875rem;">No reports uploaded yet.</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================
# MESSAGE HISTORY
# ============================================
elif page == "Message History":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">Message <span class="accent">History</span></div>
        <div class="page-subtitle">Full log of all messages sent through HOPe</div>
    </div>
    ''', unsafe_allow_html=True)

    df = messages_to_dataframe()
    if not df.empty:
        st.markdown('<div class="hope-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2.5rem;">
            <div style="color:#64748B;">No messages logged yet.</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================
# SCHEDULE
# ============================================
elif page == "Schedule":
    st.markdown('''
    <div class="fade-in">
        <div class="page-title">Scheduled <span class="accent">Messages</span></div>
        <div class="page-subtitle">Queue and automate sponsor communications</div>
    </div>
    ''', unsafe_allow_html=True)

    if st.button("📤 Send All Due Now", type="primary"):
        try:
            from worker import send_due_messages
            send_due_messages()
            st.success("✅ Due messages sent!")
            st.rerun()
        except Exception:
            st.error("Worker not available.")

    st.divider()

    with st.expander("➕ New Scheduled Message"):
        with st.form("new_schedule", clear_on_submit=True):
            sponsors_df = sponsors_to_dataframe()
            recipient   = st.selectbox("Recipient", ["Select…"] + sponsors_df["Name"].tolist())
            channel     = st.selectbox("Channel", ["Email", "WhatsApp"])
            message     = st.text_area("Message", height=120)
            col1, col2  = st.columns(2)
            with col1:
                send_date = st.date_input("Date", value=datetime.date.today() + datetime.timedelta(days=1))
            with col2:
                send_time = st.time_input("Time", value=datetime.datetime.now().time())
            send_dt = datetime.datetime.combine(send_date, send_time)
            if st.form_submit_button("Schedule", type="primary"):
                if recipient != "Select…" and message:
                    add_scheduled_message(recipient, channel, message, send_dt.isoformat())
                    st.success("✅ Scheduled!")
                    st.rerun()

    st.markdown('<div class="section-subheader">Pending</div>', unsafe_allow_html=True)
    pending_df = scheduled_messages_to_dataframe(status="pending")
    if not pending_df.empty:
        sponsors_df = sponsors_to_dataframe()
        st.markdown('<div class="hope-card">', unsafe_allow_html=True)
        for _, row in pending_df.iterrows():
            r1, r2, r3 = st.columns([4, 1, 1])
            r1.markdown(f'''
            <div style="padding:0.2rem 0;">
                <div style="font-weight:600;color:#E2E8F0;">{row["Recipient"]}</div>
                <div style="font-size:0.82rem;color:#64748B;">{str(row["Message"])[:70]}…&nbsp;&nbsp;📅 {row["Send Time"]}</div>
            </div>
            ''', unsafe_allow_html=True)
            with r2:
                if st.button("Send Now", key=f"send_{row['ID']}", type="primary"):
                    sponsor = sponsors_df[sponsors_df["Name"] == row["Recipient"]]
                    if not sponsor.empty:
                        em = sponsor.iloc[0]["Email"]
                        if row["Channel"] == "Email" and em:
                            res = send_email(em, "Scheduled", row["Message"])
                            if res.get("success"):
                                add_message(str(datetime.date.today()), row["Recipient"], "Email", "Outbound", row["Message"], "Sent")
                                update_scheduled_message_status(row["ID"], "sent")
                                st.rerun()
            with r3:
                if st.button("Cancel", key=f"cancel_{row['ID']}"):
                    update_scheduled_message_status(row["ID"], "cancelled")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="hope-card" style="text-align:center;padding:2rem;">
            <div style="color:#64748B;font-size:0.875rem;">No pending scheduled messages.</div>
        </div>
        ''', unsafe_allow_html=True)

    with st.expander("📜 History"):
        all_df = scheduled_messages_to_dataframe(status=None)
        if not all_df.empty:
            completed = all_df[all_df["Status"] != "pending"]
            if not completed.empty:
                st.markdown('<div class="hope-card">', unsafe_allow_html=True)
                st.dataframe(completed, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
