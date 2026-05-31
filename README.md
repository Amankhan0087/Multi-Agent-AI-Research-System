# ResearchMind — Multi-Agent AI Research System

> A production-ready, multi-agent AI pipeline that autonomously searches the web, scrapes sources, writes structured research reports, and critiques them — with a professional Streamlit UI, persistent user authentication, PDF export, dual LLM fallback, and Docker deployment.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-green?logo=chainlink&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-ReAct%20Agents-purple)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange)
![Mistral](https://img.shields.io/badge/Mistral-Small%20Latest-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Free](https://img.shields.io/badge/Cost-100%25%20Free-brightgreen)

---

## Overview

**ResearchMind** automates the full research lifecycle using four specialized AI agents that work in sequence. Enter any topic and get a polished, scored research report — all for free.

| Step | Agent | What it does |
|------|-------|-------------|
| 1 | **Search Agent** | Queries Tavily for 5 recent, reliable web results |
| 2 | **Reader Agent** | Picks the top URL and scrapes full-text content |
| 3 | **Writer Chain** | Drafts a structured report: Introduction, Key Findings, Conclusion, Sources |
| 4 | **Critic Chain** | Reviews the report, gives a score (X/10), strengths, and improvement areas |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ResearchMind                                 │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Streamlit Web UI                          │   │
│  │   Login/Register  →  Research Input  →  Results + PDF       │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
│                           │                                          │
│               ┌───────────▼────────────┐                            │
│               │      Auth Gate         │                            │
│               │  SQLite + bcrypt       │                            │
│               │  30-day cookie session │                            │
│               └───────────┬────────────┘                            │
│                           │                                          │
│             ┌─────────────▼──────────────────┐                      │
│             │       LLM Fallback Stack        │                      │
│             │  Groq  →  Mistral (auto-switch) │                      │
│             └─────────────┬──────────────────┘                      │
│                           │                                          │
│       ┌───────────────────┼──────────────────────────┐              │
│       ▼                   ▼                          ▼              │
│ ┌──────────────┐  ┌──────────────┐        ┌──────────────────────┐  │
│ │ Search Agent │  │ Reader Agent │        │  Writer + Critic     │  │
│ │  LangGraph   │  │  LangGraph   │        │   LCEL Chains        │  │
│ └──────┬───────┘  └──────┬───────┘        └──────────┬───────────┘  │
│        │ Tavily          │ BeautifulSoup             │ LLM          │
│        ▼                 ▼                           ▼              │
│   Web Results      Scraped Content        Report + Feedback         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Features

- **4-Step Research Pipeline** — Search → Scrape → Write → Critique, fully automated
- **Dual LLM Fallback** — Groq (Llama 3.3 70B) primary, Mistral Small fallback; auto-switches on rate limits via LangChain `with_fallbacks()`
- **Auto Rate-Limit Retry** — parses Groq's retry delay from 429 errors, waits exactly that long, shows toast notification (up to 4 attempts)
- **Connection Reset Handling** — scraper uses full browser headers + 3-attempt retry to handle bot-detection resets (Windows Error 10054)
- **Persistent Login** — 30-day browser cookie with secure server-side session tokens; same device users skip login automatically
- **User Authentication** — Register / Login / Logout with SQLite + bcrypt; session tokens stored separately from user credentials
- **Professional Streamlit UI** — dark orange theme, real-time pipeline step cards, collapsible sidebar with toggle
- **PDF Export** — download full report as formatted PDF (branded header/footer, page numbers) or Markdown
- **Docker Ready** — multi-stage Dockerfile, non-root user, health check, Compose for one-command deploy
- **100% Free Stack** — Groq, Mistral, and Tavily all on free tiers, no billing required

---

## Tech Stack

| Layer | Technology | Free Tier |
|-------|-----------|-----------|
| UI | Streamlit 1.35+ | Yes |
| Auth | SQLite + bcrypt + session tokens | Built-in |
| Persistent Login | Browser cookies via extra-streamlit-components | Built-in |
| LLM Primary | Groq — Llama 3.3 70B Versatile | 12,000 TPM |
| LLM Fallback | Mistral — mistral-small-latest | 1B tokens/month |
| Agent Framework | LangChain + LangGraph ReAct | — |
| Web Search | Tavily Search API | 1,000 searches/month |
| Web Scraping | BeautifulSoup4 + Requests | — |
| PDF Generation | fpdf2 | — |
| Containerization | Docker + Docker Compose | — |

---

## Project Structure

```
ResearchMind/
├── app.py                  # Streamlit UI — auth gate, cookie login, pipeline, PDF
├── auth.py                 # SQLite + bcrypt users + secure session token management
├── agents.py               # Groq + Mistral fallback LLMs, agent & chain definitions
├── pipeline.py             # 4-step CLI pipeline orchestrator
├── tools.py                # web_search (Tavily + retry), scrape_url (BS4 + retry)
├── main.py                 # CLI entry point (interactive + single-shot modes)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # One-command deployment
├── .dockerignore           # Excludes .venv, .env, .git from image
├── .streamlit/
│   └── config.toml         # Dark theme, server settings
└── .env                    # API keys — never committed
```

---

## Prerequisites

- Python 3.10+
- Three free API keys (no billing required on any):

| Service | Sign Up | Used For |
|---------|---------|---------|
| [Groq](https://console.groq.com/keys) | Free | Primary LLM — Llama 3.3 70B |
| [Mistral](https://console.mistral.ai/) | Free | Fallback LLM — mistral-small |
| [Tavily](https://app.tavily.com/) | Free | Web Search API |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/Amankhan0087/Multi-Agent-AI-Research-System.git
cd Multi-Agent-AI-Research-System
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create your `.env` file**

```env
GROQ_API_KEY=your_groq_api_key
MISTRAL_API_KEY=your_mistral_api_key
TAVILY_API_KEY=your_tavily_api_key
```

> `.env` is listed in `.gitignore` and is never committed.

---

## Running the App

### Streamlit Web UI (recommended)

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

**First visit** → Register an account → Login → Start researching.
**Return visits** → App opens directly (no login needed for 30 days on same device).

### CLI Mode

```bash
python pipeline.py
```

```
Enter a research topic: future of electric vehicles 2025
```

---

## Docker Deployment

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d --build
```

App available at **http://localhost:8501**

API keys are loaded from `.env` via `env_file` in `docker-compose.yml`.
User database (`users.db`) is persisted via a `./data` volume mount.

---

## Authentication System

```
Register  →  bcrypt hash stored in SQLite users table
Login     →  password verified → secure 32-char token generated
              → token saved in SQLite sessions table (30-day expiry)
              → token stored in browser cookie
Next visit →  cookie read → token validated in DB → auto-login
Sign Out  →  DB session deleted + browser cookie cleared
```

Passwords are never stored in plain text. Session tokens are cryptographically random and stored server-side — the browser only holds the token, not any user credentials.

---

## LLM Fallback

```
Every API call
      │
      ▼
  Groq — Llama 3.3 70B  ──── success ──► return result
      │
  rate limit / any error
      │
      ▼
  Mistral — mistral-small  ──► return result
```

Implemented via LangChain's `with_fallbacks()` — zero manual retry code at the chain level. Transient 429 errors also trigger an auto-wait (exact delay from Groq's error response) before the switch.

---

## Pipeline Steps

### Step 1 — Search Agent
LangGraph ReAct agent uses **Tavily** to fetch 5 recent web results. Includes 3-attempt retry for connection drops.

### Step 2 — Reader Agent
LangGraph ReAct agent picks the most relevant URL and scrapes it with **BeautifulSoup** using full Chrome browser headers (avoids bot-detection resets). 3-attempt retry with backoff.

### Step 3 — Writer Chain
LangChain LCEL chain generates a full report:
- **Introduction** — context and scope
- **Key Findings** — minimum 3 detailed points with examples
- **Conclusion** — summary and outlook
- **Sources** — all referenced URLs

### Step 4 — Critic Chain
LCEL critic chain returns a structured review:
- **Score** (X/10)
- **Strengths**
- **Areas to Improve**
- **One-line verdict**

---

## Roadmap

- [x] 4-step multi-agent research pipeline
- [x] Groq free tier LLM (Llama 3.3 70B)
- [x] Mistral Small automatic fallback (100% free)
- [x] Auto-retry: rate limits + connection resets
- [x] Professional Streamlit dark UI
- [x] Real-time pipeline step status cards
- [x] User authentication (register / login / logout)
- [x] Persistent login — 30-day cookie session
- [x] PDF + Markdown report download
- [x] Docker multi-stage build + Compose
- [ ] LangGraph parallel agent execution
- [ ] Multiple URL scraping per run
- [ ] Re-run writer if critic score < 7
- [ ] Research history per user (SQLite)
- [ ] Streamlit Cloud one-click deploy

---

## Contributing

Contributions are welcome. Please open an issue first to discuss your change, then submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by **Aman Khan**

Powered by Groq · Mistral · LangChain · LangGraph · Tavily · Streamlit
