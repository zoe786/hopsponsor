# ============================================================
#  SponsorAI – HOPe Management  |  Premium Dark Theme
# ============================================================

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

# ── Ensure data folders exist ────────────────────────────────
os.makedirs("data", exist_ok=True)
os.makedirs("data/reports", exist_ok=True)
initialize_database()

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="SponsorAI – HOPe Management",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
#  SESSION STATE
# ============================================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "selected_grade" not in st.session_state:
    st.session_state.selected_grade = None
if "selected_student" not in st.session_state:
    st.session_state.selected_student = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()


# ============================================================
#  THEME COLOR PALETTE
# ============================================================
if st.session_state.theme == "dark":
    BG          = "#0B1120"
    BG2         = "#1E293B"
    BG_INPUT    = "#0F172A"
    HOVER       = "#334155"
    TXT         = "#F1F5F9"
    TXT2        = "#94A3B8"
    ACCENT      = "#2563EB"
    ACCENT_H    = "#1D4ED8"
    SUCCESS     = "#10B981"
    WARNING     = "#F59E0B"
    ERROR       = "#EF4444"
    BORDER      = "#334155"
    SIDEBAR_BG  = "#0B1120"
    TH_BG       = "#0F172A"
    CHAT_USER   = "#2563EB"
    CHAT_BOT    = "#1E293B"
    GLOW        = "0 0 20px rgba(37,99,235,0.15)"
else:
    BG          = "#F8FAFC"
    BG2         = "#FFFFFF"
    BG_INPUT    = "#FFFFFF"
    HOVER       = "#F1F5F9"
    TXT         = "#0F172A"
    TXT2        = "#64748B"
    ACCENT      = "#2563EB"
    ACCENT_H    = "#1D4ED8"
    SUCCESS     = "#10B981"
    WARNING     = "#F59E0B"
    ERROR       = "#EF4444"
    BORDER      = "#E2E8F0"
    SIDEBAR_BG  = "#0F172A"
    TH_BG       = "#F1F5F9"
    CHAT_USER   = "#2563EB"
    CHAT_BOT    = "#F1F5F9"
    GLOW        = "0 4px 12px rgba(0,0,0,0.08)"

# ============================================================
#  FONT AWESOME (loaded via <link>)
# ============================================================
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
""", unsafe_allow_html=True)

# ============================================================
#  MASSIVE DARK / LIGHT CSS BLOCK
# ============================================================
st.markdown(f"""
<style>
/* ── Font ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, *::before, *::after {{ font-family: 'Inter', sans-serif; }}

/* ── Scrollbar ────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {TXT2}; }}

/* ── App Shell ────────────────────────────────────────── */
.stApp {{ background: {BG}; color: {TXT}; }}
.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}}

/* ── Sidebar ─────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
    padding-top: 0.5rem;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {{
    color: {TXT} !important;
}}

/* ── Sidebar Navigation (radio → nav items) ───────────── */
[data-testid="stSidebar"] [data-testid="stRadio"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label {{
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 1rem; margin: 2px 0;
    border-radius: 10px; font-size: 0.9rem; font-weight: 500;
    color: {TXT2} !important; background: transparent;
    transition: all 0.2s ease; cursor: pointer;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:hover {{
    background: rgba(37,99,235,0.10); color: {TXT} !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label > div {{
    display: none; /* hide default radio circle */
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div:has(input:checked) > label {{
    background: rgba(37,99,235,0.18) !important;
    color: #FFFFFF !important;
    font-weight: 600;
    box-shadow: inset 3px 0 0 {ACCENT};
}}

/* ── Headings ─────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{ color: {TXT} !important; font-weight: 700; }}
.stSubheader {{ color: {TXT2} !important; }}

/* ── Buttons ──────────────────────────────────────────── */
.stButton > button {{
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 0.5rem 1.25rem !important; font-size: 0.875rem !important;
    transition: all 0.2s ease !important; border: 1px solid transparent !important;
}}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stFormSubmitButton"] {{
    background: {ACCENT} !important; color: #FFF !important;
    border-color: {ACCENT} !important;
}}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stFormSubmitButton"]:hover {{
    background: {ACCENT_H} !important; border-color: {ACCENT_H} !important;
    transform: translateY(-1px); box-shadow: 0 4px 14px rgba(37,99,235,0.35);
}}
.stButton > button[kind="secondary"] {{
    background: {BG2} !important; color: {TXT} !important;
    border-color: {BORDER} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: {HOVER} !important; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}}

/* ── Text Input ───────────────────────────────────────── */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] > div > div > input {{
    background: {BG_INPUT} !important; color: {TXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 8px !important;
    padding: 0.55rem 0.85rem !important; font-size: 0.9rem !important;
    transition: border-color 0.2s ease !important;
}}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stNumberInput"] > div > div > input:focus {{
    border-color: {ACCENT} !important; box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
}}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {{
    color: {TXT2} !important; font-weight: 500 !important; font-size: 0.85rem !important;
}}

/* ── Text Area ────────────────────────────────────────── */
[data-testid="stTextArea"] > div > div > textarea {{
    background: {BG_INPUT} !important; color: {TXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 8px !important;
    padding: 0.65rem 0.85rem !important; font-size: 0.9rem !important;
    line-height: 1.6 !important; transition: border-color 0.2s ease !important;
}}
[data-testid="stTextArea"] > div > div > textarea:focus {{
    border-color: {ACCENT} !important; box-shadow: 0 0 0 2px rgba(37,99,235,0.2) !important;
}}
[data-testid="stTextArea"] label {{
    color: {TXT2} !important; font-weight: 500 !important; font-size: 0.85rem !important;
}}

/* ── Selectbox ────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {{
    background: {BG_INPUT} !important; color: {TXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 8px !important;
}}
[data-testid="stSelectbox"] label {{
    color: {TXT2} !important; font-weight: 500 !important; font-size: 0.85rem !important;
}}
[data-testid="stSelectbox"] svg {{ color: {TXT2} !important; }}

/* ── Checkbox ─────────────────────────────────────────── */
[data-testid="stCheckbox"] label {{
    color: {TXT} !important; font-size: 0.9rem !important;
}}
[data-testid="stCheckbox"] [data-baseweb="checkbox"] {{
    border-color: {BORDER} !important; background: {BG_INPUT} !important;
}}

/* ── Date / Time Input ────────────────────────────────── */
[data-testid="stDateInput"] > div > div > input,
[data-testid="stTimeInput"] > div > div > input {{
    background: {BG_INPUT} !important; color: {TXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 8px !important;
}}
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label {{
    color: {TXT2} !important; font-weight: 500 !important; font-size: 0.85rem !important;
}}

/* ── File Uploader ────────────────────────────────────── */
[data-testid="stFileUploader"] section {{
    background: {BG_INPUT} !important; border: 2px dashed {BORDER} !important;
    border-radius: 12px !important; padding: 1.5rem !important;
    transition: border-color 0.2s ease !important;
}}
[data-testid="stFileUploader"] section:hover {{
    border-color: {ACCENT} !important;
}}
[data-testid="stFileUploader"] span {{ color: {TXT2} !important; }}
[data-testid="stFileUploader"] p {{ color: {TXT2} !important; font-size: 0.85rem !important; }}

/* ── Expander ─────────────────────────────────────────── */
.streamlit-expanderHeader {{
    background: {BG2} !important; color: {TXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 12px !important;
    font-weight: 600 !important; font-size: 0.95rem !important;
    padding: 0.85rem 1.25rem !important; transition: all 0.2s ease !important;
}}
.streamlit-expanderHeader:hover {{
    border-color: {ACCENT} !important;
    box-shadow: {GLOW};
}}
[data-testid="stExpander"] details {{
    background: {BG2} !important; border: 1px solid {BORDER} !important;
    border-radius: 12px !important; overflow: hidden;
}}
[data-testid="stExpander"] details[open] {{
    border-radius: 12px 12px 12px 12px !important;
}}
[data-testid="stExpander"] details > div {{
    padding: 1rem 1.25rem !important;
}}
.streamlit-expanderIcon {{ color: {ACCENT} !important; }}

/* ── Divider ──────────────────────────────────────────── */
.stDivider {{ border-color: {BORDER} !important; margin: 1.5rem 0 !important; }}

/* ── Data Editor (Ag Grid) ────────────────────────────── */
[data-testid="stDataEditor"] {{
    background: {BG2} !important; border: 1px solid {BORDER} !important;
    border-radius: 12px !important; overflow: hidden;
}}
[data-testid="stDataEditor"] .ag-root-wrapper {{
    background: {BG2} !important; border: none !important;
    border-radius: 12px !important;
}}
[data-testid="stDataEditor"] .ag-theme-streamlit {{
    --ag-background-color: {BG2} !important;
    --ag-header-background-color: {TH_BG} !important;
    --ag-header-foreground-color: {TXT} !important;
    --ag-foreground-color: {TXT} !important;
    --ag-row-hover-color: {HOVER} !important;
    --ag-border-color: {BORDER} !important;
    --ag-input-focus-border-color: {ACCENT} !important;
    --ag-range-selection-border-color: {ACCENT} !important;
    --ag-selected-row-background-color: rgba(37,99,235,0.12) !important;
    --ag-row-border-color: {BORDER} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: 12px !important;
}}
[data-testid="stDataEditor"] .ag-header-cell-label {{
    font-weight: 600 !important; color: {TXT} !important;
}}
[data-testid="stDataEditor"] .ag-cell {{
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stDataEditor"] input {{
    background: {BG_INPUT} !important; color: {TXT} !important;
    border: 1px solid {ACCENT} !important; border-radius: 4px !important;
    padding: 2px 6px !important;
}}
[data-testid="stDataEditor"] .ag-paging-panel {{
    background: {TH_BG} !important; color: {TXT2} !important;
    border-top: 1px solid {BORDER} !important;
}}
[data-testid="stDataEditor"] button {{
    color: {TXT} !important; border-radius: 6px !important;
}}

/* ── Data Frame (read-only tables) ────────────────────── */
[data-testid="stDataFrame"] {{
    background: {BG2} !important; border: 1px solid {BORDER} !important;
    border-radius: 12px !important; overflow: hidden;
}}
[data-testid="stDataFrame"] table {{
    background: {BG2} !important; color: {TXT} !important;
    border-collapse: collapse !important; font-size: 0.875rem !important;
}}
[data-testid="stDataFrame"] th {{
    background: {TH_BG} !important; color: {TXT} !important;
    font-weight: 600 !important; padding: 0.75rem 1rem !important;
    border-bottom: 2px solid {BORDER} !important; text-align: left !important;
}}
[data-testid="stDataFrame"] td {{
    padding: 0.65rem 1rem !important; border-bottom: 1px solid {BORDER} !important;
    color: {TXT} !important;
}}
[data-testid="stDataFrame"] tr:hover td {{
    background: {HOVER} !important;
}}

/* ── Chat Input ───────────────────────────────────────── */
[data-testid="stChatInput"] {{
    background: {BG2} !important; border: 1px solid {BORDER} !important;
    border-radius: 12px !important; padding: 0.25rem !important;
}}
[data-testid="stChatInput"] textarea {{
    background: transparent !important; color: {TXT} !important;
    border: none !important; font-size: 0.9rem !important;
    padding: 0.5rem 0.75rem !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: {TXT2} !important; }}

/* ── Alerts (info / success / warning / error) ────────── */
[data-testid="stAlert"] {{
    border-radius: 10px !important; font-size: 0.875rem !important;
    padding: 0.85rem 1.15rem !important; border: 1px solid !important;
}}
[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {{
    background: rgba(37,99,235,0.08) !important;
    border-color: rgba(37,99,235,0.25) !important; color: {TXT} !important;
}}
[data-testid="stAlert"][data-baseweb="notification"][kind="success"] {{
    background: rgba(16,185,129,0.08) !important;
    border-color: rgba(16,185,129,0.25) !important; color: {TXT} !important;
}}
[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {{
    background: rgba(245,158,11,0.08) !important;
    border-color: rgba(245,158,11,0.25) !important; color: {TXT} !important;
}}
[data-testid="stAlert"][data-baseweb="notification"][kind="error"] {{
    background: rgba(239,68,68,0.08) !important;
    border-color: rgba(239,68,68,0.25) !important; color: {TXT} !important;
}}

/* ── Spinner ──────────────────────────────────────────── */
[stSpinner="true"] > div > div > div {{
    border-top-color: {ACCENT} !important;
}}

/* ── Tabs ─────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: 4px; background: transparent !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    border-radius: 8px !important; font-size: 0.875rem !important;
    font-weight: 500 !important; color: {TXT2} !important;
    background: transparent !important; padding: 0.5rem 1.25rem !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {{
    background: {HOVER} !important; color: {TXT} !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background: {ACCENT} !important; color: #FFF !important;
    font-weight: 600 !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    background: {ACCENT} !important; height: 0 !important;
}}

/* ── Popover / Dropdown ───────────────────────────────── */
[data-baseweb="popover"] {{
    background: {BG2} !important; border: 1px solid {BORDER} !important;
    border-radius: 10px !important; box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
    z-index: 9999 !important;
}}
[data-baseweb="popover"] li {{
    color: {TXT} !important; font-size: 0.875rem !important;
}}
[data-baseweb="popover"] li:hover {{
    background: {HOVER} !important;
}}

/* ── Metric Cards (custom HTML) ───────────────────────── */
.metric-card {{
    background: {BG2}; border: 1px solid {BORDER}; border-radius: 14px;
    padding: 1.35rem 1.5rem; transition: all 0.25s ease;
    position: relative; overflow: hidden;
}}
.metric-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, {ACCENT}, transparent);
    opacity: 0; transition: opacity 0.25s ease;
}}
.metric-card:hover {{
    border-color: {ACCENT}; transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(37,99,235,0.12);
}}
.metric-card:hover::before {{ opacity: 1; }}
.mc-icon {{
    width: 42px; height: 42px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; font-size: 1.15rem;
    margin-bottom: 0.75rem;
}}
.mc-icon.blue   {{ background: rgba(37,99,235,0.12); color: {ACCENT}; }}
.mc-icon.green  {{ background: rgba(16,185,129,0.12); color: {SUCCESS}; }}
.mc-icon.amber  {{ background: rgba(245,158,11,0.12); color: {WARNING}; }}
.mc-icon.red    {{ background: rgba(239,68,68,0.12); color: {ERROR}; }}
.mc-icon.purple {{ background: rgba(139,92,246,0.12); color: #8B5CF6; }}
.mc-number {{ font-size: 2rem; font-weight: 800; color: {TXT}; line-height: 1.1; }}
.mc-label {{ font-size: 0.8rem; color: {TXT2}; font-weight: 500; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; }}
.mc-trend {{
    font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem;
    padding: 0.15rem 0.6rem; border-radius: 20px; margin-top: 0.6rem;
}}
.mc-trend.up   {{ color: {SUCCESS}; background: rgba(16,185,129,0.1); }}
.mc-trend.info {{ color: {ACCENT}; background: rgba(37,99,235,0.1); }}

/* ── Section Headers (custom HTML) ────────────────────── */
.sec-header {{
    font-size: 1.6rem; font-weight: 800; color: {TXT};
    display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}}
.sec-header i {{ color: {ACCENT}; font-size: 1.3rem; }}
.sec-sub {{
    font-size: 0.9rem; color: {TXT2}; margin-bottom: 1.75rem; font-weight: 400;
}}

/* ── Hierarchy Cards (Grades / Students) ──────────────── */
.hier-card {{
    background: {BG2}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 1.15rem 1.25rem; cursor: pointer; transition: all 0.2s ease;
    margin-bottom: 0.6rem;
}}
.hier-card:hover {{
    border-color: {ACCENT}; background: {HOVER};
    transform: translateY(-2px); box-shadow: {GLOW};
}}
.hier-card .hc-title {{ font-size: 1.05rem; font-weight: 600; color: {TXT}; }}
.hier-card .hc-sub {{ font-size: 0.82rem; color: {TXT2}; margin-top: 0.15rem; }}
.hier-card .hc-badge {{
    display: inline-block; font-size: 0.7rem; font-weight: 600;
    padding: 0.1rem 0.55rem; border-radius: 20px; margin-top: 0.4rem;
    background: rgba(37,99,235,0.1); color: {ACCENT};
}}

/* ── Form Container ───────────────────────────────────── */
.form-box {{
    background: {BG2}; border: 1px solid {BORDER}; border-radius: 14px;
    padding: 1.75rem; margin: 1rem 0;
}}
.form-box h3 {{
    margin: 0 0 1.25rem 0; color: {TXT}; font-weight: 700; font-size: 1.15rem;
    padding-bottom: 0.75rem; border-bottom: 1px solid {BORDER};
    display: flex; align-items: center; gap: 0.5rem;
}}
.form-box h3 i {{ color: {ACCENT}; }}

/* ── Chat Bubbles ─────────────────────────────────────── */
.chat-bubble-wrap {{
    display: flex; gap: 0.75rem; margin-bottom: 1rem;
    align-items: flex-start;
}}
.chat-avatar {{
    width: 36px; height: 36px; border-radius: 10px; display: flex;
    align-items: center; justify-content: center; font-size: 1.1rem;
    flex-shrink: 0;
}}
.chat-avatar.user {{ background: {ACCENT}; }}
.chat-avatar.bot  {{ background: {HOVER}; }}
.chat-bubble {{
    padding: 0.85rem 1.15rem; border-radius: 14px; font-size: 0.9rem;
    line-height: 1.65; max-width: 75%; white-space: pre-wrap; word-break: break-word;
}}
.chat-bubble.user {{
    background: {CHAT_USER}; color: #FFF; border-bottom-right-radius: 4px;
}}
.chat-bubble.bot {{
    background: {CHAT_BOT}; color: {TXT}; border: 1px solid {BORDER};
    border-bottom-left-radius: 4px;
}}
.chat-bubble.draft {{
    border: 1px solid {ACCENT}; background: {BG2};
}}
.draft-actions {{
    display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.65rem;
}}
.draft-actions select {{
    background: {BG_INPUT} !important; color: {TXT} !important;
    border: 1px solid {BORDER} !important; border-radius: 8px !important;
    padding: 0.35rem 0.6rem !important; font-size: 0.8rem !important;
}}
.draft-btn {{
    padding: 0.35rem 0.85rem; border-radius: 8px; font-size: 0.78rem;
    font-weight: 600; border: 1px solid {BORDER}; background: {BG2};
    color: {TXT}; cursor: pointer; transition: all 0.2s ease; display: inline-flex;
    align-items: center; gap: 0.3rem;
}}
.draft-btn:hover {{ border-color: {ACCENT}; background: {HOVER}; }}
.draft-btn.send {{ background: {ACCENT}; color: #FFF; border-color: {ACCENT}; }}
.draft-btn.send:hover {{ background: {ACCENT_H}; }}
.draft-btn.reject {{ border-color: {ERROR}; color: {ERROR}; }}
.draft-btn.reject:hover {{ background: rgba(239,68,68,0.1); }}

/* ── Schedule Cards ───────────────────────────────────── */
.sched-card {{
    background: {BG2}; border: 1px solid {BORDER}; border-radius: 12px;
    padding: 1.15rem 1.25rem; margin-bottom: 0.65rem; transition: all 0.2s ease;
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}}
.sched-card:hover {{ border-color: {ACCENT}; box-shadow: {GLOW}; }}
.sched-card .sc-recipient {{ font-weight: 600; color: {TXT}; font-size: 0.95rem; }}
.sched-card .sc-msg {{ font-size: 0.82rem; color: {TXT2}; margin-top: 0.2rem; }}
.sched-card .sc-time {{ font-size: 0.78rem; color: {ACCENT}; font-weight: 500; margin-top: 0.3rem; }}
.sched-card .sc-actions {{ display: flex; gap: 0.5rem; flex-shrink: 0; }}

/* ── Status Badges ────────────────────────────────────── */
.badge {{
    display: inline-block; padding: 0.15rem 0.65rem; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600; text-transform: capitalize;
}}
.badge-success {{ background: rgba(16,185,129,0.12); color: {SUCCESS}; }}
.badge-warning {{ background: rgba(245,158,11,0.12); color: {WARNING}; }}
.badge-error   {{ background: rgba(239,68,68,0.12); color: {ERROR}; }}
.badge-info    {{ background: rgba(37,99,235,0.12); color: {ACCENT}; }}
.badge-default {{ background: {HOVER}; color: {TXT2}; }}

/* ── Styled HTML Table ────────────────────────────────── */
.styled-table {{
    width: 100%; border-collapse: collapse; font-size: 0.875rem;
}}
.styled-table thead th {{
    background: {TH_BG}; color: {TXT}; font-weight: 600;
    padding: 0.75rem 1rem; text-align: left;
    border-bottom: 2px solid {BORDER}; position: sticky; top: 0; z-index: 5;
}}
.styled-table tbody td {{
    padding: 0.65rem 1rem; border-bottom: 1px solid {BORDER}; color: {TXT};
}}
.styled-table tbody tr:hover td {{ background: {HOVER}; }}
.styled-table tbody tr:last-child td {{ border-bottom: none; }}
.styled-table-wrap {{
    background: {BG2}; border: 1px solid {BORDER}; border-radius: 12px;
    overflow: auto; max-height: 400px;
}}

/* ── Sidebar Logo ─────────────────────────────────────── */
.sidebar-logo {{
    font-size: 1.65rem; font-weight: 800; color: #FFF;
    padding: 0.25rem 0.5rem 1.5rem 0.5rem; letter-spacing: -0.03em;
    display: flex; align-items: center; gap: 0.55rem;
}}
.sidebar-logo .logo-icon {{
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, {ACCENT}, #7C3AED);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; color: #FFF;
}}
.sidebar-logo .ai {{ color: {ACCENT}; }}

/* ── Sidebar Stats ────────────────────────────────────── */
.sb-stat {{
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 0.65rem 0.9rem; margin-bottom: 0.45rem;
    display: flex; align-items: center; justify-content: space-between;
}}
.sb-stat .sb-label {{
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em;
    color: {TXT2}; font-weight: 500;
}}
.sb-stat .sb-num {{
    font-size: 1.15rem; font-weight: 700; color: #FFF;
}}

/* ── Sidebar Theme Toggle ─────────────────────────────── */
.sb-toggle {{
    display: flex; align-items: center; gap: 0.6rem; padding: 0.55rem 0.85rem;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; color: {TXT2}; font-size: 0.82rem; font-weight: 500;
    cursor: pointer; transition: all 0.2s ease; margin-top: 0.5rem;
}}
.sb-toggle:hover {{ background: rgba(255,255,255,0.08); color: #FFF; }}
.sb-toggle i {{ font-size: 0.95rem; color: {WARNING}; }}

/* ── Empty State ──────────────────────────────────────── */
.empty-state {{
    text-align: center; padding: 3rem 1rem; color: {TXT2};
}}
.empty-state i {{ font-size: 2.5rem; margin-bottom: 0.75rem; opacity: 0.4; }}
.empty-state .es-text {{ font-size: 0.95rem; font-weight: 500; }}

/* ── Delete Confirm ───────────────────────────────────── */
.del-confirm {{
    font-size: 0.78rem; color: {ERROR}; font-weight: 500; margin-top: 0.35rem;
}}

/* ── Utility ──────────────────────────────────────────── */
.text-accent {{ color: {ACCENT}; }}
.text-muted  {{ color: {TXT2}; }}
.mb-0 {{ margin-bottom: 0 !important; }}
.mt-1 {{ margin-top: 0.5rem; }}
.flex-between {{ display: flex; justify-content: space-between; align-items: center; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
#  HELPER: Render DataFrame as Styled HTML Table
# ============================================================
def render_styled_table(df, columns=None, max_col_width=80):
    """Render a pandas DataFrame as a premium styled HTML table."""
    if df.empty:
        return f'''<div class="empty-state">
            <i class="fa-regular fa-folder-open"></i>
            <div class="es-text">No data available</div>
        </div>'''

    if columns:
        df = df[[c for c in columns if c in df.columns]]

    html = '<div class="styled-table-wrap"><table class="styled-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = row[col]
            if col in ("Status", "status"):
                v = str(val).lower() if val else ""
                if v in ("sent", "success"):
                    cls = "badge-success"
                elif v in ("draft", "pending"):
                    cls = "badge-warning"
                elif v in ("received",):
                    cls = "badge-info"
                elif v in ("cancelled", "failed", "error"):
                    cls = "badge-error"
                else:
                    cls = "badge-default"
                html += f'<td><span class="badge {cls}">{val}</span></td>'
            else:
                s = str(val) if val is not None else ""
                s = s[:max_col_width] + "…" if len(s) > max_col_width else s
                html += f'<td>{s}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    return html


# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon"><i class="fa-solid fa-handshake-angle"></i></div>
        Sponsor<span class="ai">AI</span>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats
    sponsors_df = sponsors_to_dataframe()
    students_df = get_students()
    messages_df = messages_to_dataframe()
    pending_schedules = scheduled_messages_to_dataframe(status="pending")

    st.markdown(f"""
    <div class="sb-stat">
        <span class="sb-label"><i class="fa-solid fa-users" style="margin-right:4px;"></i> Sponsors</span>
        <span class="sb-num">{len(sponsors_df)}</span>
    </div>
    <div class="sb-stat">
        <span class="sb-label"><i class="fa-solid fa-graduation-cap" style="margin-right:4px;"></i> Students</span>
        <span class="sb-num">{len(students_df)}</span>
    </div>
    <div class="sb-stat">
        <span class="sb-label"><i class="fa-solid fa-clock" style="margin-right:4px;"></i> Pending</span>
        <span class="sb-num">{len(pending_schedules)}</span>
    </div>
    """, unsafe_allow_html=True)

    # Theme Toggle
    theme_icon = "fa-moon" if st.session_state.theme == "light" else "fa-sun"
    theme_text = "Dark Mode" if st.session_state.theme == "light" else "Light Mode"
    if st.button(f"  {theme_text}", key="theme_btn", use_container_width=True):
        toggle_theme()

    st.markdown(f"""
    <style>
        [data-testid="stSidebar"] button[key="theme_btn"] {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            color: {TXT2} !important; border-radius: 10px !important;
            font-weight: 500 !important; font-size: 0.82rem !important;
            padding: 0.55rem 0.85rem !important; margin-top: 0.35rem !important;
            display: flex !important; align-items: center !important;
        }}
        [data-testid="stSidebar"] button[key="theme_btn"]:hover {{
            background: rgba(255,255,255,0.08) !important; color: #FFF !important;
        }}
    </style>
    <script>
        // Inject FA icon into theme button
        var tb = document.querySelector('[data-testid="stSidebar"] button[key="theme_btn"]');
        if(tb) tb.innerHTML = '<i class="fa-solid {theme_icon}" style="color:{WARNING};margin-right:6px;"></i>{theme_text}';
    </script>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Sponsors", "Students", "Assistant", "Message History", "Schedule"],
        index=0,
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(f"""
    <div style="padding:0 0.5rem;">
        <span style="font-size:0.7rem;color:{TXT2};text-transform:uppercase;letter-spacing:0.06em;font-weight:500;">
            <i class="fa-solid fa-circle" style="font-size:0.4rem;color:{SUCCESS};vertical-align:middle;margin-right:4px;"></i>
            v2.0 — SaaS Edition
        </span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
#  PAGE: DASHBOARD
# ============================================================
if page == "Dashboard":
    st.markdown('<div class="sec-header"><i class="fa-solid fa-chart-line"></i> Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Overview of your sponsor ecosystem</div>', unsafe_allow_html=True)

    reports_count = len(get_reports())
    sent_count = len(messages_df[messages_df["Status"] == "Sent"]) if not messages_df.empty else 0
    pending_count = len(pending_schedules)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-icon blue"><i class="fa-solid fa-users"></i></div>
            <div class="mc-number">{len(sponsors_df)}</div>
            <div class="mc-label">Sponsors</div>
            <div class="mc-trend up"><i class="fa-solid fa-arrow-up" style="font-size:0.6rem;"></i> {len(sponsors_df)} total</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-icon green"><i class="fa-solid fa-graduation-cap"></i></div>
            <div class="mc-number">{len(students_df)}</div>
            <div class="mc-label">Students</div>
            <div class="mc-trend up"><i class="fa-solid fa-arrow-up" style="font-size:0.6rem;"></i> {len(students_df)} total</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-icon amber"><i class="fa-solid fa-file-lines"></i></div>
            <div class="mc-number">{reports_count}</div>
            <div class="mc-label">Reports</div>
            <div class="mc-trend info"><i class="fa-solid fa-file-arrow-up" style="font-size:0.6rem;"></i> uploaded</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-icon purple"><i class="fa-solid fa-paper-plane"></i></div>
            <div class="mc-number">{sent_count}</div>
            <div class="mc-label">Sent</div>
            <div class="mc-trend up"><i class="fa-solid fa-check" style="font-size:0.6rem;"></i> delivered</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="mc-icon red"><i class="fa-solid fa-clock"></i></div>
            <div class="mc-number">{pending_count}</div>
            <div class="mc-label">Scheduled</div>
            <div class="mc-trend info"><i class="fa-solid fa-hourglass-half" style="font-size:0.6rem;"></i> pending</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="sec-header" style="font-size:1.15rem;"><i class="fa-solid fa-list-check"></i> Recent Activity</div>', unsafe_allow_html=True)
    if not messages_df.empty:
        st.markdown(
            render_styled_table(messages_df.head(8), ["Date", "Recipient", "Channel", "Direction", "Status"]),
            unsafe_allow_html=True
        )
    else:
        st.markdown(f'''
        <div class="empty-state">
            <i class="fa-regular fa-clock"></i>
            <div class="es-text">No recent activity yet</div>
        </div>''', unsafe_allow_html=True)


# ============================================================
#  PAGE: SPONSORS
# ============================================================
elif page == "Sponsors":
    st.markdown('<div class="sec-header"><i class="fa-solid fa-users"></i> Sponsors</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Editable table — click any cell to modify</div>', unsafe_allow_html=True)

    df = sponsors_to_dataframe()

    with st.expander("Add New Sponsor", expanded=False):
        with st.form("add_sponsor_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", key="sp_name")
                new_company = st.text_input("Company", key="sp_company")
            with col2:
                new_email = st.text_input("Email", key="sp_email")
                new_whatsapp = st.text_input("WhatsApp", key="sp_whatsapp")
            new_notes = st.text_area("Notes", key="sp_notes")
            if st.form_submit_button("Add Sponsor", use_container_width=True):
                if new_name:
                    add_sponsor(new_name, new_company, new_whatsapp, new_email, new_notes)
                    st.success("Sponsor added successfully!")
                    st.rerun()
                else:
                    st.warning("Name is required.")

    if not df.empty:
        display_df = df.drop(columns=["ID"])

        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            num_rows="dynamic",
            key="sponsor_editor",
            hide_index=True,
            column_config={
                "Name":    st.column_config.TextColumn("Name", required=True),
                "Company": st.column_config.TextColumn("Company"),
                "Email":   st.column_config.TextColumn("Email"),
                "WhatsApp":st.column_config.TextColumn("WhatsApp"),
                "Notes":   st.column_config.TextColumn("Notes"),
            }
        )

        col_save, col_del = st.columns([1, 1])
        with col_save:
            if st.button("Save All Changes", use_container_width=True, type="primary"):
                for idx, row in edited_df.iterrows():
                    original_row = df[df["Name"] == row["Name"]]
                    if not original_row.empty:
                        sid = original_row.iloc[0]["ID"]
                        update_sponsor(sid, row["Name"], row["Company"], row["WhatsApp"], row["Email"], row["Notes"])
                st.success("All changes saved!")
                st.rerun()

        with col_del:
            del_name = st.selectbox("Select sponsor to delete:", ["— None —"] + df["Name"].tolist(), key="sp_del_sel")
            if del_name != "— None —":
                confirm_del = st.checkbox("I confirm this deletion", key="sp_del_confirm")
                if st.button("Delete Selected", use_container_width=True):
                    if confirm_del:
                        sponsor_row = df[df["Name"] == del_name].iloc[0]
                        delete_sponsor(sponsor_row["ID"])
                        st.success(f"Deleted {del_name}.")
                        st.rerun()
                    else:
                        st.error("Please check the confirmation box first.")
    else:
        st.markdown(f'''
        <div class="empty-state">
            <i class="fa-regular fa-address-book"></i>
            <div class="es-text">No sponsors yet. Add one above.</div>
        </div>''', unsafe_allow_html=True)


# ============================================================
#  PAGE: STUDENTS (Grade → Student → Profile)
# ============================================================
elif page == "Students":
    st.markdown('<div class="sec-header"><i class="fa-solid fa-graduation-cap"></i> Students</div>', unsafe_allow_html=True)

    students_all = get_students()
    grades = get_grades()

    # ── LEVEL 1: Grade Selection ─────────────────────────
    if st.session_state.selected_grade is None:
        st.markdown('<div class="sec-sub">Select a grade to view students</div>', unsafe_allow_html=True)

        grades_list = grades["name"].tolist()
        cols = st.columns(4)
        for i, grade in enumerate(grades_list):
            with cols[i % 4]:
                count = len(students_all[students_all["grade_name"] == grade])
                st.markdown(f'''
                <div class="hier-card">
                    <div class="hc-title"><i class="fa-solid fa-folder" style="color:{ACCENT};margin-right:6px;font-size:0.9rem;"></i>{grade}</div>
                    <div class="hc-sub">{count} student{"s" if count != 1 else ""}</div>
                    <span class="hc-badge">{count}</span>
                </div>''', unsafe_allow_html=True)
                if st.button(f"Open {grade}", key=f"grade_{grade}", use_container_width=True):
                    st.session_state.selected_grade = grade
                    st.session_state.selected_student = None
                    st.rerun()

        with st.expander("Add New Student", expanded=False):
            with st.form("add_student_form"):
                c1, c2 = st.columns(2)
                with c1:
                    s_name = st.text_input("Full Name", key="stu_name")
                    s_age = st.number_input("Age", min_value=1, max_value=100, step=1, key="stu_age")
                with c2:
                    s_grade_name = st.selectbox("Grade", grades_list, key="stu_grade")
                    s_grade_id = grades[grades["name"] == s_grade_name]["id"].iloc[0]
                s_contact = st.text_input("Contact Info (phone / email)", key="stu_contact")
                s_address = st.text_area("Address", key="stu_addr")
                sp_df = sponsors_to_dataframe()
                sp_opts = ["— None —"] + sp_df["Name"].tolist()
                s_sp_name = st.selectbox("Sponsor", sp_opts, key="stu_sp")
                s_sp_id = None
                if s_sp_name != "— None —":
                    s_sp_id = sp_df[sp_df["Name"] == s_sp_name]["ID"].iloc[0]
                s_auto = st.checkbox("Auto-send reports to sponsor", value=True, key="stu_auto")
                s_notes = st.text_area("Notes (optional)", key="stu_notes")
                if st.form_submit_button("Add Student", use_container_width=True):
                    if s_name:
                        code = add_student(s_name, s_age, s_contact, s_address, s_grade_id, s_sp_id, s_auto, s_notes)
                        st.success(f"Student {s_name} added ({code})!")
                        st.rerun()
                    else:
                        st.warning("Please enter a name.")

    # ── LEVEL 2: Student Selection ───────────────────────
    elif st.session_state.selected_grade is not None and st.session_state.selected_student is None:
        grade = st.session_state.selected_grade

        if st.button("← Back to Grades"):
            st.session_state.selected_grade = None
            st.rerun()

        st.markdown(f'<div class="sec-header" style="font-size:1.3rem;"><i class="fa-solid fa-book-open"></i> {grade}</div>', unsafe_allow_html=True)

        grade_students = students_all[students_all["grade_name"] == grade]

        if not grade_students.empty:
            cols = st.columns(3)
            for i, (idx, stu) in enumerate(grade_students.iterrows()):
                with cols[i % 3]:
                    sp_text = stu["sponsor_name"] if stu["sponsor_name"] else "Unassigned"
                    st.markdown(f'''
                    <div class="hier-card">
                        <div class="hc-title"><i class="fa-solid fa-user" style="color:{ACCENT};margin-right:6px;font-size:0.85rem;"></i>{stu["name"]}</div>
                        <div class="hc-sub">{stu["student_code"]}</div>
                        <div class="hc-sub"><i class="fa-solid fa-handshake" style="margin-right:4px;font-size:0.7rem;"></i>{sp_text}</div>
                    </div>''', unsafe_allow_html=True)
                    if st.button(f"View {stu['name']}", key=f"student_{stu['id']}", use_container_width=True):
                        st.session_state.selected_student = stu["id"]
                        st.rerun()
        else:
            st.info(f"No students in {grade} yet.")
            with st.expander("Add Student to this Grade", expanded=True):
                with st.form("add_student_grade_form"):
                    s_name = st.text_input("Full Name", key="stu_g_name")
                    s_age = st.number_input("Age", min_value=1, max_value=100, step=1, key="stu_g_age")
                    s_contact = st.text_input("Contact Info", key="stu_g_contact")
                    s_address = st.text_area("Address", key="stu_g_addr")
                    g_id = grades[grades["name"] == grade]["id"].iloc[0]
                    sp_df = sponsors_to_dataframe()
                    sp_opts = ["— None —"] + sp_df["Name"].tolist()
                    s_sp_name = st.selectbox("Sponsor", sp_opts, key="stu_g_sp")
                    s_sp_id = None
                    if s_sp_name != "— None —":
                        s_sp_id = sp_df[sp_df["Name"] == s_sp_name]["ID"].iloc[0]
                    s_auto = st.checkbox("Auto-send reports", value=True, key="stu_g_auto")
                    s_notes = st.text_area("Notes", key="stu_g_notes")
                    if st.form_submit_button("Add Student", use_container_width=True):
                        if s_name:
                            code = add_student(s_name, s_age, s_contact, s_address, g_id, s_sp_id, s_auto, s_notes)
                            st.success(f"Student {s_name} added!")
                            st.rerun()

    # ── LEVEL 3: Student Profile ─────────────────────────
    elif st.session_state.selected_student is not None:
        sid = st.session_state.selected_student

        # Get full student data with JOINs
        stu_full = students_all[students_all["id"] == sid]
        stu_base = get_student(sid)

        if stu_full.empty or stu_base is None:
            st.error("Student not found.")
            st.session_state.selected_student = None
            st.rerun()
        else:
            student = stu_full.iloc[0].to_dict()
            student["sponsor_id"] = stu_base["sponsor_id"]
            student["grade_id"] = stu_base["grade_id"]

            # Back buttons
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button("← Back to Students"):
                    st.session_state.selected_student = None
                    st.rerun()
            with bc2:
                if st.button("← Back to Grades"):
                    st.session_state.selected_grade = None
                    st.session_state.selected_student = None
                    st.rerun()

            # Profile Header
            st.markdown(f'''
            <div class="form-box">
                <h3><i class="fa-solid fa-id-card"></i> Student Profile — {student["name"]}</h3>
                <p style="color:{TXT2};margin:0;font-size:0.85rem;">
                    <i class="fa-solid fa-barcode" style="margin-right:4px;"></i>
                    Code: <strong style="color:{TXT};">{student["student_code"]}</strong>
                </p>
            </div>''', unsafe_allow_html=True)

            # Edit Form
            with st.form("student_profile_form"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    p_name = st.text_input("Full Name", value=student["name"], key="prof_name")
                    p_age = st.number_input("Age", value=student["age"], min_value=1, max_value=100, step=1, key="prof_age")
                    p_contact = st.text_input("Contact Info", value=student["contact_info"], key="prof_contact")
                with fc2:
                    g_all = get_grades()
                    g_opts = g_all["name"].tolist()
                    cur_g = student.get("grade_name", "")
                    g_idx = g_opts.index(cur_g) if cur_g in g_opts else 0
                    p_grade_name = st.selectbox("Grade", g_opts, index=g_idx, key="prof_grade")
                    p_grade_id = g_all[g_all["name"] == p_grade_name]["id"].iloc[0]

                    sp_df = sponsors_to_dataframe()
                    sp_opts = ["— None —"] + sp_df["Name"].tolist()
                    cur_sp = student.get("sponsor_name") or "— None —"
                    sp_idx = sp_opts.index(cur_sp) if cur_sp in sp_opts else 0
                    p_sp_name = st.selectbox("Sponsor", sp_opts, index=sp_idx, key="prof_sp")
                    p_sp_id = None if p_sp_name == "— None —" else sp_df[sp_df["Name"] == p_sp_name]["ID"].iloc[0]

                p_address = st.text_area("Address", value=student["address"], key="prof_addr")
                p_auto = st.checkbox("Auto-send reports to sponsor", value=bool(student["auto_send"]), key="prof_auto")
                p_notes = st.text_area("Notes", value=student["notes"], key="prof_notes")

                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    if st.form_submit_button("Save Changes", use_container_width=True, type="primary"):
                        update_student(sid, p_name, p_age, p_contact, p_address, p_grade_id, p_sp_id, p_auto, p_notes)
                        st.success("Student updated!")
                        st.rerun()
                with ac2:
                    if st.form_submit_button("Delete Student", use_container_width=True):
                        if st.checkbox("Confirm permanent deletion", key="prof_del_conf"):
                            delete_student(sid)
                            st.success("Student deleted.")
                            st.session_state.selected_student = None
                            st.rerun()
                with ac3:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.selected_student = None
                        st.rerun()

            # ── Reports Section ──────────────────────────
            st.divider()
            st.markdown('<div class="sec-header" style="font-size:1.1rem;"><i class="fa-solid fa-file-lines"></i> Reports</div>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Upload a report for this student",
                type=["pdf", "png", "jpg", "jpeg", "docx"],
                key=f"report_{sid}"
            )
            if uploaded_file:
                if st.button("Upload and Send to Sponsor", type="primary", use_container_width=True):
                    ext = uploaded_file.name.split(".")[-1]
                    safe_name = f"{student['student_code']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    file_path = os.path.join("data/reports", safe_name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    report_id = add_report(sid, file_path, uploaded_file.name)

                    if student["auto_send"] and student.get("sponsor_id"):
                        sponsor = get_sponsor(student["sponsor_id"])
                        if sponsor and sponsor.get("email"):
                            body = f"""
<div style="font-family:Inter,sans-serif;color:#1E293B;">
<p>Dear {sponsor['name']},</p>
<p>A new report for <strong>{student['name']}</strong> (Grade: {student.get('grade_name', 'N/A')}) is now available.</p>
<table style="font-size:0.9rem;margin:1rem 0;">
<tr><td style="padding:4px 12px 4px 0;color:#64748B;">Age:</td><td>{student['age']}</td></tr>
<tr><td style="padding:4px 12px 4px 0;color:#64748B;">Contact:</td><td>{student['contact_info']}</td></tr>
<tr><td style="padding:4px 12px 4px 0;color:#64748B;">Address:</td><td>{student['address']}</td></tr>
</table>
<p>Please find the attached report.</p>
<p style="color:#64748B;font-size:0.85rem;">— SponsorAI</p>
</div>"""
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
                            st.warning("Report uploaded but sponsor has no email.")
                    else:
                        st.success("Report uploaded (auto-send disabled or no sponsor assigned).")

            reports = get_reports(sid)
            if not reports.empty:
                st.markdown('<div class="sec-sub" style="margin-top:1rem;margin-bottom:0.75rem;">Previous Reports</div>', unsafe_allow_html=True)
                st.markdown(
                    render_styled_table(reports, ["file_name", "upload_date", "message_sent", "sent_to"]),
                    unsafe_allow_html=True
                )


# ============================================================
#  PAGE: ASSISTANT
# ============================================================
elif page == "Assistant":
    st.markdown('<div class="sec-header"><i class="fa-solid fa-robot"></i> Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Chat with AI or generate message drafts</div>', unsafe_allow_html=True)

    mode = st.radio("Mode", ["Chat", "Draft"], horizontal=True, index=0, key="assist_mode")

    uploaded_image = st.file_uploader(
        "Upload image (optional — for event flyers, posters, etc.)",
        type=["png", "jpg", "jpeg"],
        key="assistant_img"
    )

    # Render existing messages
    for msg in st.session_state.messages:
        role = msg["role"]
        is_draft = msg.get("is_draft", False)
        processed = msg.get("processed", False)

        avatar_class = "user" if role == "user" else "bot"
        avatar_icon = '<i class="fa-solid fa-user"></i>' if role == "user" else '<i class="fa-solid fa-robot"></i>'
        bubble_class = "user" if role == "user" else ("draft" if is_draft and not processed else "bot")

        with st.container():
            st.markdown(f'''
            <div class="chat-bubble-wrap">
                <div class="chat-avatar {avatar_class}">{avatar_icon}</div>
                <div>
                    <div class="chat-bubble {bubble_class}">{msg["content"]}</div>''', unsafe_allow_html=True)

            # Draft actions
            if is_draft and not processed:
                sponsors_df = sponsors_to_dataframe()
                st.markdown(f'''
                    <div class="draft-actions">
                        <select id="ch_{msg['id']}">
                            <option value="Email">Email</option>
                            <option value="WhatsApp">WhatsApp</option>
                        </select>
                        <select id="rec_{msg['id']}">
                            <option value="Select...">Select recipient...</option>
                            {"".join(f'<option value="{n}">{n}</option>' for n in sponsors_df["Name"].tolist())}
                        </select>
                    </div>
                    <div class="draft-actions" style="margin-top:0.4rem;">''', unsafe_allow_html=True)

                da1, da2, da3, da4 = st.columns(4)
                with da1:
                    if st.button("Send Now", key=f"send_{msg['id']}", use_container_width=True, type="primary"):
                        # Read from selectbox widgets below
                        ch = st.session_state.get(f"drch_{msg['id']}", "Email")
                        rec = st.session_state.get(f"drrec_{msg['id']}", "Select...")
                        if rec and rec != "Select...":
                            sp_row = sponsors_df[sponsors_df["Name"] == rec].iloc[0]
                            email = sp_row["Email"]
                            if ch == "Email" and email:
                                res = send_email(email, "Message from SponsorAI", msg["content"])
                                if res.get("success"):
                                    add_message(str(datetime.date.today()), rec, "Email", "Outbound", msg["content"], "Sent")
                                    msg["processed"] = True
                                    msg["content"] += "\n\n✅ Sent."
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {res.get('error')}")
                            elif ch == "WhatsApp" and sp_row.get("WhatsApp"):
                                res = send_whatsapp(sp_row["WhatsApp"], msg["content"])
                                if res.get("success"):
                                    add_message(str(datetime.date.today()), rec, "WhatsApp", "Outbound", msg["content"], "Sent")
                                    msg["processed"] = True
                                    msg["content"] += "\n\n✅ Sent via WhatsApp."
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {res.get('error')}")
                            else:
                                st.warning("No contact info for this channel.")
                        else:
                            st.warning("Select a recipient.")
                with da2:
                    if st.button("Schedule", key=f"sch_{msg['id']}", use_container_width=True):
                        ch = st.session_state.get(f"drch_{msg['id']}", "Email")
                        rec = st.session_state.get(f"drrec_{msg['id']}", "Select...")
                        if rec and rec != "Select...":
                            st.session_state["sched_draft"] = msg["content"]
                            st.session_state["sched_recipient"] = rec
                            st.session_state["sched_channel"] = ch
                            st.session_state["sched_id"] = msg["id"]
                            st.rerun()
                        else:
                            st.warning("Select a recipient first.")
                with da3:
                    if st.button("Save Draft", key=f"save_{msg['id']}", use_container_width=True):
                        rec = st.session_state.get(f"drrec_{msg['id']}", "Draft")
                        ch = st.session_state.get(f"drch_{msg['id']}", "Email")
                        add_message(str(datetime.date.today()), rec, ch, "Outbound", msg["content"], "Draft")
                        msg["processed"] = True
                        msg["content"] += "\n\n📝 Saved as draft."
                        st.rerun()
                with da4:
                    if st.button("Reject", key=f"rej_{msg['id']}", use_container_width=True):
                        msg["processed"] = True
                        msg["content"] += "\n\n❌ Rejected."
                        st.rerun()

                # Hidden selectboxes for Streamlit state
                ch_val = st.selectbox("Channel", ["Email", "WhatsApp"], key=f"drch_{msg['id']}", label_visibility="collapsed")
                rec_val = st.selectbox("Recipient", ["Select..."] + sponsors_df["Name"].tolist(), key=f"drrec_{msg['id']}", label_visibility="collapsed")

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)

    # Schedule expander (from draft)
    if "sched_draft" in st.session_state:
        with st.expander("Schedule Message", expanded=True):
            sc1, sc2 = st.columns(2)
            with sc1:
                send_date = st.date_input("Date", value=datetime.date.today() + datetime.timedelta(days=1), key="sch_date")
            with sc2:
                send_time = st.time_input("Time", value=datetime.datetime.now().time(), key="sch_time")
            send_dt = datetime.datetime.combine(send_date, send_time)
            if st.button("Confirm Schedule", type="primary", use_container_width=True):
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
                for k in ["sched_draft", "sched_recipient", "sched_channel", "sched_id"]:
                    st.session_state.pop(k, None)
                st.success("Message scheduled!")
                st.rerun()
            if st.button("Cancel", use_container_width=True):
                for k in ["sched_draft", "sched_recipient", "sched_channel", "sched_id"]:
                    st.session_state.pop(k, None)
                st.rerun()

    # Chat Input
    prompt = st.chat_input("Type your message...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        if mode == "Chat":
            styles_df = styles_to_dataframe()
            style_text = "\n".join(styles_df["Message"].astype(str)) if not styles_df.empty else ""
            img_data = uploaded_image.read() if uploaded_image else None
            with st.spinner("Thinking…"):
                response = chat_assistant(st.session_state.messages, style_text, img_data)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        else:
            img_desc = ""
            if uploaded_image:
                with st.spinner("Analyzing image…"):
                    img_desc = describe_image(uploaded_image.read())
            styles_df = styles_to_dataframe()
            style_text = "\n".join(styles_df["Message"].astype(str)) if not styles_df.empty else ""
            with st.spinner("Generating draft…"):
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


# ============================================================
#  PAGE: MESSAGE HISTORY
# ============================================================
elif page == "Message History":
    st.markdown('<div class="sec-header"><i class="fa-solid fa-clock-rotate-left"></i> Message History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">All sent, received, and drafted messages</div>', unsafe_allow_html=True)

    df = messages_to_dataframe()
    if not df.empty:
        st.markdown(
            render_styled_table(df, ["Date", "Recipient", "Channel", "Direction", "Message", "Status"], max_col_width=60),
            unsafe_allow_html=True
        )
    else:
        st.markdown(f'''
        <div class="empty-state">
            <i class="fa-regular fa-envelope"></i>
            <div class="es-text">No messages yet</div>
        </div>''', unsafe_allow_html=True)


# ============================================================
#  PAGE: SCHEDULE
# ============================================================
elif page == "Schedule":
    st.markdown('<div class="sec-header"><i class="fa-solid fa-calendar-check"></i> Scheduled Messages</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Manage pending and past scheduled messages</div>', unsafe_allow_html=True)

    if st.button("Send Due Now", type="primary", use_container_width=True):
        try:
            from worker import send_due_messages
            send_due_messages()
            st.success("Due messages processed!")
            st.rerun()
        except Exception:
            st.error("Worker not available. Make sure worker.py is running separately.")

    st.divider()

    # New Schedule Form
    with st.expander("New Schedule", expanded=False):
        with st.form("new_schedule"):
            sp_df = sponsors_to_dataframe()
            sch_recipient = st.selectbox("Recipient", ["Select..."] + sp_df["Name"].tolist())
            sch_channel = st.selectbox("Channel", ["Email", "WhatsApp"])
            sch_message = st.text_area("Message")
            sc1, sc2 = st.columns(2)
            with sc1:
                sch_date = st.date_input("Date", value=datetime.date.today() + datetime.timedelta(days=1), key="ns_date")
            with sc2:
                sch_time = st.time_input("Time", value=datetime.datetime.now().time(), key="ns_time")
            sch_dt = datetime.datetime.combine(sch_date, sch_time)
            if st.form_submit_button("Schedule Message", type="primary", use_container_width=True):
                if sch_recipient != "Select..." and sch_message:
                    add_scheduled_message(sch_recipient, sch_channel, sch_message, sch_dt.isoformat())
                    st.success("Message scheduled!")
                    st.rerun()
                else:
                    st.warning("Recipient and message are required.")

    # Pending List
    st.markdown('<div class="sec-header" style="font-size:1.1rem;"><i class="fa-solid fa-hourglass-half"></i> Pending</div>', unsafe_allow_html=True)

    pending_df = scheduled_messages_to_dataframe(status="pending")
    sp_df = sponsors_to_dataframe()

    if not pending_df.empty:
        for _, row in pending_df.iterrows():
            with st.container():
                msg_preview = str(row["Message"])[:70] + ("…" if len(str(row["Message"])) > 70 else "")
                st.markdown(f'''
                <div class="sched-card">
                    <div>
                        <div class="sc-recipient"><i class="fa-solid fa-user" style="color:{ACCENT};margin-right:6px;font-size:0.8rem;"></i>{row["Recipient"]}</div>
                        <div class="sc-msg">{msg_preview}</div>
                        <div class="sc-time"><i class="fa-regular fa-clock" style="margin-right:4px;"></i>{row["Send Time"]}</div>
                    </div>
                    <div class="sc-actions">
                        <span class="badge badge-warning"><i class="fa-solid fa-hourglass" style="margin-right:3px;font-size:0.6rem;"></i> Pending</span>
                    </div>
                </div>''', unsafe_allow_html=True)

                sa1, sa2 = st.columns(2)
                with sa1:
                    if st.button("Send Now", key=f"send_{row['ID']}", use_container_width=True, type="primary"):
                        sp_match = sp_df[sp_df["Name"] == row["Recipient"]]
                        if not sp_match.empty:
                            sp_row = sp_match.iloc[0]
                            if row["Channel"] == "Email" and sp_row.get("Email"):
                                res = send_email(sp_row["Email"], "Scheduled Message", row["Message"])
                                if res.get("success"):
                                    add_message(str(datetime.date.today()), row["Recipient"], "Email", "Outbound", row["Message"], "Sent")
                                    update_scheduled_message_status(row["ID"], "sent")
                                    st.success("Sent!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {res.get('error')}")
                            elif row["Channel"] == "WhatsApp" and sp_row.get("WhatsApp"):
                                res = send_whatsapp(sp_row["WhatsApp"], row["Message"])
                                if res.get("success"):
                                    add_message(str(datetime.date.today()), row["Recipient"], "WhatsApp", "Outbound", row["Message"], "Sent")
                                    update_scheduled_message_status(row["ID"], "sent")
                                    st.success("Sent via WhatsApp!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {res.get('error')}")
                            else:
                                st.warning("No contact info for this channel.")
                        else:
                            st.warning("Sponsor not found.")
                with sa2:
                    if st.button("Cancel", key=f"cancel_{row['ID']}", use_container_width=True):
                        update_scheduled_message_status(row["ID"], "cancelled")
                        st.success("Cancelled.")
                        st.rerun()
    else:
        st.markdown(f'''
        <div class="empty-state">
            <i class="fa-regular fa-calendar"></i>
            <div class="es-text">No pending schedules</div>
        </div>''', unsafe_allow_html=True)

    # History
    with st.expander("History"):
        all_df = scheduled_messages_to_dataframe(status=None)
        if not all_df.empty:
            hist_df = all_df[all_df["Status"] != "pending"]
            st.markdown(
                render_styled_table(hist_df, ["Recipient", "Channel", "Message", "Send Time", "Status"], max_col_width=60),
                unsafe_allow_html=True
            )
        else:
            st.info("No history yet.")