"""
ResearchMind — Streamlit Frontend
Multi-Agent AI Research Pipeline powered by Groq + LangGraph
"""

import streamlit as st
import time
import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Retry helper ─────────────────────────────────────────────────────────────
def run_with_retry(fn, label: str, max_retries: int = 4):
    """Auto-retry on Groq 429 rate-limit errors using the delay Groq provides."""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            err = str(e)
            if "429" in err and "rate_limit" in err.lower():
                match = re.search(r"try again in (\d+(?:\.\d+)?)s", err)
                wait = float(match.group(1)) + 1.0 if match else 6.0
                if attempt < max_retries - 1:
                    st.toast(f"⏳ Rate limit on {label} — retrying in {wait:.0f}s…")
                    time.sleep(wait)
                    continue
            raise  # non-429 errors bubble up immediately


# ── Page config ───────────────────────────────────────────────────────────────
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

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}
.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1300px; }

/* Hero */
.hero { text-align: center; padding: 3rem 0 2rem; }
.hero-eyebrow {
    font-family: 'DM Mono', monospace; font-size: 0.7rem;
    font-weight: 500; letter-spacing: 0.25em; text-transform: uppercase;
    color: #ff8c32; margin-bottom: 1rem; opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 4.5rem);
    font-weight: 800; line-height: 1.0; letter-spacing: -0.03em;
    color: #f0ebe0; margin: 0 0 1rem;
}
.hero h1 span { color: #ff8c32; }
.hero-sub {
    font-size: 1rem; font-weight: 300; color: #a09890;
    max-width: 520px; margin: 0 auto; line-height: 1.65;
}
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
}

/* Input card */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important; color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    color: #ff8c32 !important; font-weight: 500 !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    letter-spacing: 0.04em !important; border: none !important;
    border-radius: 10px !important; padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important; width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important; opacity: 0.95 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Step cards */
.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 0.9rem;
    position: relative; overflow: hidden; transition: border-color 0.3s;
}
.step-card.active  { border-color: rgba(255,140,50,0.4); background: rgba(255,140,50,0.05); }
.step-card.done    { border-color: rgba(80,200,120,0.3); background: rgba(80,200,120,0.03); }
.step-card.error   { border-color: rgba(255,80,80,0.4); background: rgba(255,80,80,0.04); }
.step-card::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
    border-radius: 14px 0 0 14px; background: rgba(255,255,255,0.05); transition: background 0.3s;
}
.step-card.active::before { background: #ff8c32; }
.step-card.done::before   { background: #50c878; }
.step-card.error::before  { background: #ff5050; }

.step-header { display:flex; align-items:center; gap:0.8rem; margin-bottom:0.2rem; }
.step-num {
    font-family: 'DM Mono', monospace; font-size: 0.65rem;
    font-weight: 500; letter-spacing: 0.15em; color: #ff8c32; opacity: 0.7;
}
.step-title { font-family: 'Syne', sans-serif; font-size: 0.9rem; font-weight: 700; color: #f0ebe0; }
.step-status { margin-left: auto; font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.1em; }
.status-waiting { color: #444; }
.status-running { color: #ff8c32; }
.status-done    { color: #50c878; }
.status-error   { color: #ff5050; }

/* Result panels */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.5rem 1.8rem; margin: 0.5rem 0 1rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 500;
    letter-spacing: 0.2em; text-transform: uppercase; color: #ff8c32;
    margin-bottom: 0.8rem; padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.88rem; line-height: 1.8; color: #cdc8bf;
    white-space: pre-wrap; font-family: 'DM Sans', sans-serif;
}

/* Report & feedback */
.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px; padding: 2rem 2.5rem; margin-top: 0.5rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.2);
    border-radius: 16px; padding: 2rem 2.5rem; margin-top: 0.5rem;
}
.panel-label {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 1.2rem; padding-bottom: 0.6rem;
}
.panel-label.orange { color: #ff8c32; border-bottom: 1px solid rgba(255,140,50,0.15); }
.panel-label.green  { color: #50c878; border-bottom: 1px solid rgba(80,200,120,0.15); }

/* Error box */
.error-box {
    background: rgba(255,80,80,0.08);
    border: 1px solid rgba(255,80,80,0.3);
    border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1rem 0;
    font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #ff9090; line-height: 1.6;
}

/* Section heading */
.section-heading {
    font-family: 'Syne', sans-serif; font-size: 1.1rem;
    font-weight: 700; color: #f0ebe0; margin: 0 0 0.8rem;
}

/* Progress bar override */
.stProgress > div > div > div > div { background: #ff8c32 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem; }

/* Download button */
.stDownloadButton > button {
    background: rgba(255,140,50,0.1) !important;
    border: 1px solid rgba(255,140,50,0.3) !important;
    color: #ff8c32 !important; font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important; letter-spacing: 0.08em !important;
    border-radius: 8px !important; padding: 0.5rem 1.2rem !important;
    width: auto !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,140,50,0.18) !important;
    transform: translateY(-1px) !important;
}

.notice {
    font-family: 'DM Mono', monospace; font-size: 0.68rem;
    color: #333; text-align: center; margin-top: 3rem; letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
# current_step: 0=idle  1=searching  2=reading  3=writing  4=critiquing  5=done
_defaults = {
    "current_step": 0,
    "results": {},
    "topic": "",
    "error": None,
    "start_time": None,
    "elapsed": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def step_state(step_num: int) -> str:
    cs = st.session_state.current_step
    if st.session_state.error and cs == 0:
        return "error" if step_num == st.session_state.get("_failed_step", -1) else "waiting"
    if cs == 0 and not st.session_state.results:
        return "waiting"
    if cs == 5 or (cs == 0 and st.session_state.results):
        return "done"
    if step_num < cs:
        return "done"
    if step_num == cs:
        return "running"
    return "waiting"


def render_step(num_str: str, title: str, desc: str, state: str):
    status_map = {
        "waiting": ("WAITING",    "status-waiting"),
        "running": ("● RUNNING",  "status-running"),
        "done":    ("✓ DONE",     "status-done"),
        "error":   ("✗ ERROR",    "status-error"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done", "error": "error"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num_str}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        <div style="font-size:0.78rem;color:#504840;margin-top:0.2rem;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def reset():
    st.session_state.current_step = 0
    st.session_state.results = {}
    st.session_state.error = None
    st.session_state.start_time = None
    st.session_state.elapsed = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:#f0ebe0;margin-bottom:0.3rem;">
        Research<span style="color:#ff8c32;">Mind</span>
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#555;letter-spacing:0.15em;margin-bottom:2rem;">
        MULTI-AGENT AI SYSTEM
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#ff8c32;letter-spacing:0.15em;margin-bottom:0.8rem;">
    HOW IT WORKS
    </div>
    """, unsafe_allow_html=True)

    steps_info = [
        ("🔍", "Search Agent", "Queries Tavily for the 5 most relevant web sources"),
        ("📄", "Reader Agent", "Scrapes the top URL for full-text deep content"),
        ("✍️", "Writer Chain", "Drafts a structured report from combined data"),
        ("🧐", "Critic Chain", "Scores and reviews the report for quality"),
    ]
    for icon, name, desc in steps_info:
        st.markdown(f"""
        <div style="display:flex;gap:0.7rem;margin-bottom:1rem;align-items:flex-start;">
            <span style="font-size:1rem;margin-top:0.1rem;">{icon}</span>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:700;color:#e0dbd2;">{name}</div>
                <div style="font-size:0.75rem;color:#605850;line-height:1.5;margin-top:0.1rem;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.05);margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#ff8c32;letter-spacing:0.15em;margin-bottom:0.8rem;">
    POWERED BY
    </div>
    """, unsafe_allow_html=True)

    tech = [("🤖", "Groq", "Llama 3.3 70B Versatile"),
            ("🔗", "LangGraph", "ReAct Agent Framework"),
            ("🌐", "Tavily", "Real-time Web Search"),
            ("🕷️", "BeautifulSoup", "Web Content Scraper")]
    for icon, name, detail in tech:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
            <span style="font-size:0.8rem;color:#a09890;">{icon} {name}</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#504840;">{detail}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.elapsed:
        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.05);margin:1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#555;letter-spacing:0.1em;">
            LAST RUN · {st.session_state.elapsed:.1f}s
        </div>
        """, unsafe_allow_html=True)


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


# ── Main layout ───────────────────────────────────────────────────────────────
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
        run_btn = st.button(
            "⚡  Run Research Pipeline",
            use_container_width=True,
            disabled=st.session_state.current_step not in (0, 5),
        )
    with btn_col2:
        if st.session_state.results or st.session_state.error:
            if st.button("↺ Reset", use_container_width=True):
                reset()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#504840;letter-spacing:0.12em;">TRY →</span>
    """, unsafe_allow_html=True)
    for ex in ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress", "Climate tech startups"]:
        st.markdown(f"""
        <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
            border-radius:6px;padding:0.22rem 0.65rem;font-size:0.73rem;color:#a09890;
            font-family:'DM Sans',sans-serif;">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Error display
    if st.session_state.error:
        st.markdown(f'<div class="error-box">⚠ Pipeline Error<br><br>{st.session_state.error}</div>',
                    unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline Status</div>', unsafe_allow_html=True)
    render_step("01", "Search Agent",  "Gathers recent web information",      step_state(1))
    render_step("02", "Reader Agent",  "Scrapes & extracts deep content",      step_state(2))
    render_step("03", "Writer Chain",  "Drafts the full research report",      step_state(3))
    render_step("04", "Critic Chain",  "Reviews & scores the report",          step_state(4))

    # Progress bar during execution
    if st.session_state.current_step in (1, 2, 3, 4):
        progress = (st.session_state.current_step - 1) / 4
        st.progress(progress)
        step_labels = {1: "Searching the web…", 2: "Scraping content…",
                       3: "Writing report…",    4: "Reviewing report…"}
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#ff8c32;
             letter-spacing:0.1em;margin-top:0.5rem;">
            {step_labels[st.session_state.current_step]}
        </div>
        """, unsafe_allow_html=True)


# ── Trigger: start pipeline ───────────────────────────────────────────────────
if run_btn:
    if not topic_input.strip():
        st.warning("Please enter a research topic first.")
    else:
        reset()
        st.session_state.topic = topic_input.strip()
        st.session_state.current_step = 1
        st.session_state.start_time = time.time()
        st.rerun()


# ── Execute current step ──────────────────────────────────────────────────────
cs = st.session_state.current_step

if cs == 1:
    try:
        agent = build_search_agent()
        result = run_with_retry(
            lambda: agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {st.session_state.topic}")]
            }),
            "Search Agent",
        )
        st.session_state.results["search"] = result["messages"][-1].content
        st.session_state.current_step = 2
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state._failed_step = 1
        st.session_state.current_step = 0
    st.rerun()

elif cs == 2:
    try:
        agent = build_reader_agent()
        result = run_with_retry(
            lambda: agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{st.session_state.topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{st.session_state.results['search'][:600]}"
                )]
            }),
            "Reader Agent",
        )
        st.session_state.results["reader"] = result["messages"][-1].content
        st.session_state.current_step = 3
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state._failed_step = 2
        st.session_state.current_step = 0
    st.rerun()

elif cs == 3:
    try:
        research = (
            f"SEARCH RESULTS:\n{st.session_state.results['search'][:1000]}\n\n"
            f"SCRAPED CONTENT:\n{st.session_state.results['reader'][:800]}"
        )
        st.session_state.results["writer"] = run_with_retry(
            lambda: writer_chain.invoke({
                "topic": st.session_state.topic,
                "research": research,
            }),
            "Writer Chain",
        )
        st.session_state.current_step = 4
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state._failed_step = 3
        st.session_state.current_step = 0
    st.rerun()

elif cs == 4:
    try:
        st.session_state.results["critic"] = run_with_retry(
            lambda: critic_chain.invoke({
                "report": st.session_state.results["writer"]
            }),
            "Critic Chain",
        )
        st.session_state.current_step = 5
        st.session_state.elapsed = time.time() - st.session_state.start_time
    except Exception as e:
        st.session_state.error = str(e)
        st.session_state._failed_step = 4
        st.session_state.current_step = 0
    st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r and st.session_state.current_step in (0, 5):
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if st.session_state.elapsed:
        st.markdown(f"""
        <div style="text-align:center;font-family:'DM Mono',monospace;font-size:0.7rem;
             color:#605850;margin-bottom:1.5rem;letter-spacing:0.1em;">
            ✓ PIPELINE COMPLETE · {st.session_state.elapsed:.1f}s · TOPIC: {st.session_state.topic.upper()}
        </div>
        """, unsafe_allow_html=True)

    # Raw outputs collapsed
    col_raw1, col_raw2 = st.columns(2)
    with col_raw1:
        if "search" in r:
            with st.expander("🔍 Search Agent Output", expanded=False):
                st.markdown(
                    f'<div class="result-panel">'
                    f'<div class="result-panel-title">Raw Search Results</div>'
                    f'<div class="result-content">{r["search"]}</div>'
                    f'</div>', unsafe_allow_html=True)
    with col_raw2:
        if "reader" in r:
            with st.expander("📄 Reader Agent Output", expanded=False):
                st.markdown(
                    f'<div class="result-panel">'
                    f'<div class="result-panel-title">Scraped Content</div>'
                    f'<div class="result-content">{r["reader"]}</div>'
                    f'</div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        dl_col, _ = st.columns([1, 3])
        with dl_col:
            st.download_button(
                label="⬇  Download Report (.md)",
                data=r["writer"],
                file_name=f"research_{st.session_state.topic[:30].replace(' ','_')}_{int(time.time())}.md",
                mime="text/markdown",
            )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Groq Llama 3.3 70B · LangGraph ReAct · Tavily Search · Built with Streamlit
</div>
""", unsafe_allow_html=True)
