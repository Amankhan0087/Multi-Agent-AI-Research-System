"""
ResearchMind — Streamlit Frontend
Multi-Agent AI Research Pipeline · Groq + Gemini fallback · Auth + PDF export
"""

import streamlit as st
import time, re
from datetime import datetime
import extra_streamlit_components as stx
from auth import init_db, register_user, login_user, create_session, get_session_user, delete_session
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

COOKIE_NAME = "researchmind_session"
COOKIE_DAYS = 30

# ── DB init ───────────────────────────────────────────────────────────────────
init_db()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #e8e4dc; }

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

/* Hide toolbar/deploy button but KEEP sidebar toggle visible */
#MainMenu                        { visibility: hidden; }
footer                           { visibility: hidden; }
[data-testid="stToolbar"]        { visibility: hidden; }
[data-testid="stDecoration"]     { display: none; }

/* Sidebar toggle — always visible and styled */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    background: rgba(255,140,50,0.12) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    color: #ff8c32 !important;
    transition: background 0.2s !important;
}
[data-testid="collapsedControl"]:hover {
    background: rgba(255,140,50,0.25) !important;
}

.block-container { padding: 2rem 3rem 4rem; max-width: 1300px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem; }

/* ── Hero ── */
.hero { text-align: center; padding: 2.5rem 0 1.8rem; }
.hero-eyebrow {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    letter-spacing: 0.25em; text-transform: uppercase;
    color: #ff8c32; margin-bottom: 1rem; opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.6rem, 5.5vw, 4.2rem);
    font-weight: 800; line-height: 1.0; letter-spacing: -0.03em;
    color: #f0ebe0; margin: 0 0 0.8rem;
}
.hero h1 span { color: #ff8c32; }
.hero-sub {
    font-size: 0.98rem; font-weight: 300; color: #a09890;
    max-width: 500px; margin: 0 auto; line-height: 1.65;
}
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 1.8rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px; padding: 1.8rem 2.2rem; margin-bottom: 1.2rem;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important; color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    padding: 0.75rem 1rem !important; transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    color: #ff8c32 !important; font-weight: 500 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 0.92rem !important;
    letter-spacing: 0.04em !important; border: none !important;
    border-radius: 10px !important; padding: 0.65rem 1.8rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important; width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Step cards ── */
.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.1rem 1.4rem; margin-bottom: 0.8rem;
    position: relative; overflow: hidden; transition: border-color 0.3s;
}
.step-card.active { border-color: rgba(255,140,50,0.4); background: rgba(255,140,50,0.05); }
.step-card.done   { border-color: rgba(80,200,120,0.3); background: rgba(80,200,120,0.03); }
.step-card.error  { border-color: rgba(255,80,80,0.4);  background: rgba(255,80,80,0.04); }
.step-card::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
    border-radius:14px 0 0 14px; background:rgba(255,255,255,0.05); transition:background 0.3s;
}
.step-card.active::before { background:#ff8c32; }
.step-card.done::before   { background:#50c878; }
.step-card.error::before  { background:#ff5050; }

.step-header { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.15rem; }
.step-num  { font-family:'DM Mono',monospace; font-size:0.63rem; letter-spacing:0.15em; color:#ff8c32; opacity:0.7; }
.step-title{ font-family:'Syne',sans-serif; font-size:0.88rem; font-weight:700; color:#f0ebe0; }
.step-status{ margin-left:auto; font-family:'DM Mono',monospace; font-size:0.63rem; letter-spacing:0.1em; }
.status-waiting{ color:#3a3832; }
.status-running{ color:#ff8c32; }
.status-done   { color:#50c878; }
.status-error  { color:#ff5050; }

/* ── Result panels ── */
.result-panel {
    background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.07);
    border-radius:14px; padding:1.4rem 1.7rem; margin:0.4rem 0 0.9rem;
}
.result-panel-title {
    font-family:'DM Mono',monospace; font-size:0.67rem; letter-spacing:0.2em;
    text-transform:uppercase; color:#ff8c32; margin-bottom:0.7rem;
    padding-bottom:0.55rem; border-bottom:1px solid rgba(255,140,50,0.15);
}
.result-content{ font-size:0.87rem; line-height:1.8; color:#cdc8bf; white-space:pre-wrap; }

.report-panel {
    background:rgba(255,255,255,0.025); border:1px solid rgba(255,140,50,0.2);
    border-radius:16px; padding:1.8rem 2.2rem; margin-top:0.4rem;
}
.feedback-panel {
    background:rgba(255,255,255,0.025); border:1px solid rgba(80,200,120,0.2);
    border-radius:16px; padding:1.8rem 2.2rem; margin-top:0.4rem;
}
.panel-label {
    font-family:'DM Mono',monospace; font-size:0.67rem; letter-spacing:0.2em;
    text-transform:uppercase; margin-bottom:1.1rem; padding-bottom:0.6rem;
}
.panel-label.orange{ color:#ff8c32; border-bottom:1px solid rgba(255,140,50,0.15); }
.panel-label.green { color:#50c878; border-bottom:1px solid rgba(80,200,120,0.15); }

/* ── Error box ── */
.error-box {
    background:rgba(255,80,80,0.08); border:1px solid rgba(255,80,80,0.3);
    border-radius:12px; padding:1.1rem 1.4rem; margin:0.8rem 0;
    font-family:'DM Mono',monospace; font-size:0.78rem; color:#ff9090; line-height:1.6;
}

/* ── Auth page ── */
.auth-card {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,140,50,0.15);
    border-radius:20px; padding:2.5rem 3rem; max-width:480px; margin:0 auto;
    backdrop-filter:blur(12px);
}
.auth-logo {
    font-family:'Syne',sans-serif; font-size:2rem; font-weight:800;
    color:#f0ebe0; text-align:center; margin-bottom:0.3rem;
}
.auth-logo span { color:#ff8c32; }
.auth-sub {
    font-family:'DM Mono',monospace; font-size:0.65rem; letter-spacing:0.2em;
    text-transform:uppercase; color:#504840; text-align:center; margin-bottom:2rem;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background:rgba(255,140,50,0.1) !important;
    border:1px solid rgba(255,140,50,0.3) !important;
    color:#ff8c32 !important; font-family:'DM Mono',monospace !important;
    font-size:0.75rem !important; letter-spacing:0.08em !important;
    border-radius:8px !important; padding:0.45rem 1.1rem !important;
    width:auto !important;
}
.stDownloadButton > button:hover {
    background:rgba(255,140,50,0.2) !important; transform:translateY(-1px) !important;
}

/* ── Progress ── */
.stProgress > div > div > div > div { background:#ff8c32 !important; }

.section-heading {
    font-family:'Syne',sans-serif; font-size:1.05rem;
    font-weight:700; color:#f0ebe0; margin:0 0 0.7rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,0.03) !important;
    border-radius:10px !important; padding:4px !important;
    border:1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family:'DM Mono',monospace !important; font-size:0.75rem !important;
    letter-spacing:0.1em !important; color:#706860 !important;
    border-radius:7px !important; padding:0.4rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background:rgba(255,140,50,0.15) !important;
    color:#ff8c32 !important;
}

.notice {
    font-family:'DM Mono',monospace; font-size:0.65rem;
    color:#282420; text-align:center; margin-top:3rem; letter-spacing:0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def run_with_retry(fn, label: str, max_retries: int = 4):
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            err = str(e)
            # Groq / Mistral rate limit — wait exact delay they report
            if "429" in err and "rate_limit" in err.lower():
                match = re.search(r"try again in (\d+(?:\.\d+)?)s", err)
                wait  = float(match.group(1)) + 1.0 if match else 6.0
                if attempt < max_retries - 1:
                    st.toast(f"⏳ Rate limit on {label} — retrying in {wait:.0f}s…")
                    time.sleep(wait)
                    continue
            # Network / connection reset errors — brief backoff then retry
            elif any(x in err for x in ["ConnectionResetError", "10054", "Connection aborted",
                                         "RemoteDisconnected", "ConnectionError"]):
                wait = 3 * (attempt + 1)
                if attempt < max_retries - 1:
                    st.toast(f"🔌 Connection reset on {label} — retrying in {wait}s…")
                    time.sleep(wait)
                    continue
            raise


def render_step(num: str, title: str, desc: str, state: str):
    status_map = {
        "waiting": ("WAITING",   "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",    "status-done"),
        "error":   ("✗ ERROR",   "status-error"),
    }
    label, cls  = status_map.get(state, ("", ""))
    card_cls    = {"running":"active","done":"done","error":"error"}.get(state,"")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        <div style="font-size:0.75rem;color:#3e3830;margin-top:0.15rem;">{desc}</div>
    </div>""", unsafe_allow_html=True)


def step_state(n: int) -> str:
    cs = st.session_state.current_step
    if st.session_state.error and cs == 0:
        return "error" if n == st.session_state.get("_failed_step") else "waiting"
    if cs == 0 and not st.session_state.results: return "waiting"
    if cs == 5 or (cs == 0 and st.session_state.results): return "done"
    if n < cs:  return "done"
    if n == cs: return "running"
    return "waiting"


def generate_pdf(topic: str, report: str, feedback: str) -> bytes:
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(255, 140, 50)
            self.cell(0, 8, "ResearchMind - AI Research Report", align="C")
            self.ln(2)
            self.set_draw_color(255, 140, 50)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def footer(self):
            self.set_y(-14)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(160, 160, 160)
            self.cell(0, 6,
                f"Generated by ResearchMind · {datetime.now().strftime('%B %d, %Y')}  |  Page {self.page_no()}",
                align="C")

    def _clean(text: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*",     r"\1", text)
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
        text = re.sub(r"`(.*?)`",       r"\1", text)
        # Replace common Unicode chars that Latin-1 / Helvetica can't handle
        replacements = {
            "—": "-", "–": "-", "‒": "-",
            "‘": "'", "’": "'", "“": '"', "”": '"',
            "·": ".", "•": "-", "…": "...",
            "â€™": "'",
        }
        for ch, rep in replacements.items():
            text = text.replace(ch, rep)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Title block
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, "Research Report", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, f"Topic: {_clean(topic)}", ln=True)
    pdf.ln(3)

    # Report body
    for line in report.split("\n"):
        line = line.rstrip()
        if not line:
            pdf.ln(3); continue
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 15); pdf.set_text_color(255, 140, 50)
            pdf.multi_cell(0, 9, _clean(line[2:])); pdf.set_text_color(30, 30, 30)
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13); pdf.set_text_color(255, 140, 50)
            pdf.multi_cell(0, 8, _clean(line[3:])); pdf.set_text_color(30, 30, 30)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 7, _clean(line[4:])); pdf.set_text_color(30, 30, 30)
        elif line.startswith(("- ", "* ", "+ ")):
            pdf.set_font("Helvetica", "", 10); pdf.set_text_color(30, 30, 30)
            pdf.cell(6); pdf.multi_cell(0, 6, f"  {_clean(line[2:])}")
        elif line.startswith("**") and line.endswith("**"):
            pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 7, _clean(line[2:-2]))
        else:
            pdf.set_font("Helvetica", "", 10); pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, _clean(line))

    # Critic feedback page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(80, 200, 120)
    pdf.cell(0, 10, "Critic Feedback", ln=True)
    pdf.set_draw_color(80, 200, 120)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    for line in feedback.split("\n"):
        if line.strip():
            pdf.multi_cell(0, 6, _clean(line.strip()))
        else:
            pdf.ln(3)

    return bytes(pdf.output())


def reset_pipeline():
    st.session_state.current_step = 0
    st.session_state.results      = {}
    st.session_state.error        = None
    st.session_state.start_time   = None
    st.session_state.elapsed      = None


# ── Cookie manager (persistent login) ────────────────────────────────────────
cookie_manager = stx.CookieManager(key="researchmind_cm")

# ── Session state ─────────────────────────────────────────────────────────────
_defaults = {
    "authenticated": False,
    "username":      "",
    "session_token": "",
    "current_step":  0,
    "results":       {},
    "error":         None,
    "start_time":    None,
    "elapsed":       None,
    "auth_success":  "",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Auto-login from saved cookie ──────────────────────────────────────────────
if not st.session_state.authenticated:
    saved_token = cookie_manager.get(COOKIE_NAME)
    if saved_token:
        username = get_session_user(saved_token)
        if username:
            st.session_state.authenticated = True
            st.session_state.username      = username
            st.session_state.session_token = saved_token


# ══════════════════════════════════════════════════════════════════════════════
# AUTH GATE — show login/register if not authenticated
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:

    # Centre the card with empty columns
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style="padding:3rem 0 1rem;">
            <div class="auth-logo">Research<span>Mind</span></div>
            <div class="auth-sub">Multi-Agent AI Research System</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.auth_success:
            st.success(st.session_state.auth_success)
            st.session_state.auth_success = ""

        tab_login, tab_register = st.tabs(["  Sign In  ", "  Create Account  "])

        # ── Login tab ────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            email_in    = st.text_input("Email",    key="li_email",    placeholder="you@example.com")
            password_in = st.text_input("Password", key="li_password", placeholder="••••••••", type="password")
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

            if st.button("Sign In", key="btn_login", use_container_width=True):
                if not email_in or not password_in:
                    st.error("Please fill in all fields.")
                else:
                    ok, username, msg = login_user(email_in, password_in)
                    if ok:
                        from datetime import timedelta
                        token = create_session(username, days=COOKIE_DAYS)
                        cookie_manager.set(
                            COOKIE_NAME, token,
                            expires_at=datetime.now() + timedelta(days=COOKIE_DAYS),
                        )
                        st.session_state.authenticated = True
                        st.session_state.username      = username
                        st.session_state.session_token = token
                        st.rerun()
                    else:
                        st.error(msg)

        # ── Register tab ─────────────────────────────────────────────────────
        with tab_register:
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            reg_name  = st.text_input("Full Name",        key="reg_name",  placeholder="Aman Khan")
            reg_email = st.text_input("Email",            key="reg_email", placeholder="you@example.com")
            reg_pass  = st.text_input("Password",         key="reg_pass",  placeholder="Min. 6 characters", type="password")
            reg_pass2 = st.text_input("Confirm Password", key="reg_pass2", placeholder="Repeat password",   type="password")
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

            if st.button("Create Account", key="btn_register", use_container_width=True):
                if not all([reg_name, reg_email, reg_pass, reg_pass2]):
                    st.error("Please fill in all fields.")
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(reg_name, reg_email, reg_pass)
                    if ok:
                        st.session_state.auth_success = msg
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("""
        <div class="notice" style="margin-top:2rem;">
            ResearchMind · Groq + Gemini · LangGraph · Streamlit
        </div>""", unsafe_allow_html=True)

    st.stop()   # ← nothing below renders until user is logged in


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP (authenticated users only)
# ══════════════════════════════════════════════════════════════════════════════

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
         color:#f0ebe0;margin-bottom:0.2rem;">
        Research<span style="color:#ff8c32;">Mind</span>
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#504840;
         letter-spacing:0.15em;margin-bottom:1.5rem;">MULTI-AGENT AI SYSTEM</div>
    <div style="background:rgba(255,140,50,0.08);border:1px solid rgba(255,140,50,0.2);
         border-radius:10px;padding:0.7rem 1rem;margin-bottom:1.5rem;
         font-family:'DM Mono',monospace;font-size:0.72rem;color:#ff8c32;">
        👤 {st.session_state.username}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;
        color:#ff8c32;letter-spacing:0.15em;margin-bottom:0.8rem;">HOW IT WORKS</div>""",
        unsafe_allow_html=True)

    for icon, name, desc in [
        ("🔍", "Search Agent",  "Queries Tavily for the 5 most relevant web sources"),
        ("📄", "Reader Agent",  "Scrapes the top URL for full-text deep content"),
        ("✍️", "Writer Chain", "Drafts a structured report from combined research"),
        ("🧐", "Critic Chain",  "Scores and reviews the report for quality"),
    ]:
        st.markdown(f"""
        <div style="display:flex;gap:0.65rem;margin-bottom:0.9rem;align-items:flex-start;">
            <span style="font-size:0.95rem;margin-top:0.05rem;">{icon}</span>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:0.8rem;font-weight:700;
                     color:#e0dbd2;">{name}</div>
                <div style="font-size:0.72rem;color:#504840;line-height:1.5;margin-top:0.05rem;">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.05);margin:1.2rem 0;"></div>',
                unsafe_allow_html=True)

    for icon, name, detail in [
        ("🤖", "Groq",         "Llama 3.3 70B (primary)"),
        ("🌀", "Mistral",      "Small Latest (fallback)"),
        ("🔗", "LangGraph",    "ReAct Agents"),
        ("🌐", "Tavily",       "Real-time Search"),
    ]:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <span style="font-size:0.78rem;color:#a09890;">{icon} {name}</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#3e3830;">{detail}</span>
        </div>""", unsafe_allow_html=True)

    if st.session_state.elapsed:
        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.05);margin:1.2rem 0;"></div>',
                    unsafe_allow_html=True)
        st.markdown(f"""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;
            color:#3e3830;letter-spacing:0.08em;">LAST RUN · {st.session_state.elapsed:.1f}s</div>""",
            unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.05);margin:1.2rem 0;"></div>',
                unsafe_allow_html=True)

    if st.button("Sign Out", key="btn_logout", use_container_width=True):
        # Delete server-side session token and browser cookie
        delete_session(st.session_state.get("session_token", ""))
        cookie_manager.delete(COOKIE_NAME)
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_gap, col_pipeline = st.columns([5, 0.4, 3.5])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic_input = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_field",
        disabled=st.session_state.current_step not in (0, 5),
    )
    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True,
                            disabled=st.session_state.current_step not in (0, 5))
    with btn_col2:
        if st.session_state.results or st.session_state.error:
            if st.button("↺ Reset", use_container_width=True):
                reset_pipeline(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""<div style="display:flex;gap:0.45rem;flex-wrap:wrap;align-items:center;margin-bottom:1.2rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.63rem;color:#3e3830;letter-spacing:0.12em;">TRY →</span>""",
        unsafe_allow_html=True)
    for ex in ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress", "Climate tech startups"]:
        st.markdown(f"""<span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
            border-radius:6px;padding:0.2rem 0.6rem;font-size:0.71rem;color:#a09890;">{ex}</span>""",
            unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.error:
        st.markdown(f'<div class="error-box">⚠ Pipeline Error<br><br>{st.session_state.error}</div>',
                    unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline Status</div>', unsafe_allow_html=True)
    render_step("01", "Search Agent",  "Gathers recent web information",   step_state(1))
    render_step("02", "Reader Agent",  "Scrapes & extracts deep content",  step_state(2))
    render_step("03", "Writer Chain",  "Drafts the full research report",  step_state(3))
    render_step("04", "Critic Chain",  "Reviews & scores the report",      step_state(4))

    cs = st.session_state.current_step
    if cs in (1, 2, 3, 4):
        st.progress((cs - 1) / 4)
        labels = {1:"Searching the web…",2:"Scraping content…",3:"Writing report…",4:"Reviewing report…"}
        st.markdown(f"""<div style="font-family:'DM Mono',monospace;font-size:0.65rem;
            color:#ff8c32;letter-spacing:0.1em;margin-top:0.4rem;">{labels[cs]}</div>""",
            unsafe_allow_html=True)


# ── Trigger ───────────────────────────────────────────────────────────────────
if run_btn:
    if not topic_input.strip():
        st.warning("Please enter a research topic first.")
    else:
        reset_pipeline()
        st.session_state.topic      = topic_input.strip()
        st.session_state.current_step = 1
        st.session_state.start_time   = time.time()
        st.rerun()


# ── Execute pipeline steps ────────────────────────────────────────────────────
cs = st.session_state.current_step

if cs == 1:
    try:
        agent  = build_search_agent()
        result = run_with_retry(
            lambda: agent.invoke({"messages":[("user",
                f"Find recent, reliable and detailed information about: {st.session_state.topic}")]}),
            "Search Agent")
        st.session_state.results["search"] = result["messages"][-1].content
        st.session_state.current_step = 2
    except Exception as e:
        st.session_state.error = str(e); st.session_state._failed_step = 1; st.session_state.current_step = 0
    st.rerun()

elif cs == 2:
    try:
        agent  = build_reader_agent()
        result = run_with_retry(
            lambda: agent.invoke({"messages":[("user",
                f"Based on the following search results about '{st.session_state.topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{st.session_state.results['search'][:600]}")]}),
            "Reader Agent")
        st.session_state.results["reader"] = result["messages"][-1].content
        st.session_state.current_step = 3
    except Exception as e:
        st.session_state.error = str(e); st.session_state._failed_step = 2; st.session_state.current_step = 0
    st.rerun()

elif cs == 3:
    try:
        research = (f"SEARCH RESULTS:\n{st.session_state.results['search'][:1000]}\n\n"
                    f"SCRAPED CONTENT:\n{st.session_state.results['reader'][:800]}")
        st.session_state.results["writer"] = run_with_retry(
            lambda: writer_chain.invoke({"topic":st.session_state.topic,"research":research}),
            "Writer Chain")
        st.session_state.current_step = 4
    except Exception as e:
        st.session_state.error = str(e); st.session_state._failed_step = 3; st.session_state.current_step = 0
    st.rerun()

elif cs == 4:
    try:
        st.session_state.results["critic"] = run_with_retry(
            lambda: critic_chain.invoke({"report":st.session_state.results["writer"]}),
            "Critic Chain")
        st.session_state.current_step = 5
        st.session_state.elapsed = time.time() - st.session_state.start_time
    except Exception as e:
        st.session_state.error = str(e); st.session_state._failed_step = 4; st.session_state.current_step = 0
    st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r and st.session_state.current_step in (0, 5):
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if st.session_state.elapsed:
        st.markdown(f"""<div style="text-align:center;font-family:'DM Mono',monospace;font-size:0.68rem;
             color:#504840;margin-bottom:1.3rem;letter-spacing:0.1em;">
             ✓ COMPLETE · {st.session_state.elapsed:.1f}s · {st.session_state.topic.upper()}
        </div>""", unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if "search" in r:
            with st.expander("🔍 Search Agent Output", expanded=False):
                st.markdown(f'<div class="result-panel"><div class="result-panel-title">Raw Search Results</div>'
                            f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)
    with col_r2:
        if "reader" in r:
            with st.expander("📄 Reader Agent Output", expanded=False):
                st.markdown(f'<div class="result-panel"><div class="result-panel-title">Scraped Content</div>'
                            f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown('<div class="report-panel"><div class="panel-label orange">📝 Final Research Report</div>',
                    unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download buttons
        dl1, dl2, _ = st.columns([1, 1, 3])
        topic_slug = st.session_state.topic[:28].replace(" ", "_")
        ts = int(time.time())

        with dl1:
            st.download_button(
                "⬇  Markdown (.md)",
                data=r["writer"],
                file_name=f"report_{topic_slug}_{ts}.md",
                mime="text/markdown",
            )
        with dl2:
            if "critic" in r:
                pdf_bytes = generate_pdf(
                    st.session_state.topic, r["writer"], r["critic"]
                )
                st.download_button(
                    "⬇  PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"report_{topic_slug}_{ts}.pdf",
                    mime="application/pdf",
                )

    if "critic" in r:
        st.markdown('<div class="feedback-panel"><div class="panel-label green">🧐 Critic Feedback</div>',
                    unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Groq Llama 3.3 70B + Mistral Small · LangGraph ReAct · Tavily · Streamlit
</div>""", unsafe_allow_html=True)
