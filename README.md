# ResearchMind — Multi-Agent AI Research System

> A production-ready, multi-agent AI pipeline that autonomously searches the web, scrapes sources, writes structured research reports, and critiques them — with a professional Streamlit UI, user authentication, PDF export, and Docker deployment.

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

**ResearchMind** automates the full research lifecycle using four specialized AI agents that work in sequence. Enter any topic and the system delivers a polished, scored research report — completely free.

| Step | Agent | What it does |
|------|-------|-------------|
| 1 | **Search Agent** | Queries Tavily for 5 recent, reliable web results |
| 2 | **Reader Agent** | Picks the top URL and scrapes full-text content |
| 3 | **Writer Chain** | Drafts a structured report with Introduction, Key Findings, Conclusion, Sources |
| 4 | **Critic Chain** | Reviews the report, gives a score (X/10), strengths, and improvement areas |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        ResearchMind                                  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Streamlit Web UI                          │    │
│  │   Login / Register  →  Research Input  →  Results + PDF    │    │
│  └───────────────────────────┬─────────────────────────────────┘    │
│                              │                                       │
│                    ┌─────────▼──────────┐                           │
│                    │   Auth Gate        │  SQLite + bcrypt           │
│                    └─────────┬──────────┘                           │
│                              │                                       │
│              ┌───────────────▼──────────────────┐                   │
│              │         LLM Fallback Stack        │                   │
│              │   Groq (primary, 12k TPM free)    │                   │
│              │      ↓ on rate limit              │                   │
│              │   Mistral (fallback, 1B/mo free)  │                   │
│              └───────────────┬──────────────────┘                   │
│                              │                                       │
│        ┌─────────────────────┼──────────────────────────┐           │
│        ▼                     ▼                          ▼           │
│  ┌──────────────┐    ┌──────────────┐          ┌──────────────────┐ │
│  │ Search Agent │    │ Reader Agent │          │  Writer + Critic │ │
│  │  (LangGraph) │    │  (LangGraph) │          │  (LCEL Chains)   │ │
│  └──────┬───────┘    └──────┬───────┘          └────────┬─────────┘ │
│         │ Tavily API        │ BeautifulSoup             │ LLM       │
│         ▼                   ▼                           ▼           │
│    Web Results        Scraped Content         Report + Feedback     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Features

- **4-Step Research Pipeline** — Search → Scrape → Write → Critique, fully automated
- **Dual LLM Fallback** — Groq (Llama 3.3 70B) as primary, Mistral Small as fallback; switches automatically on rate limits via LangChain `with_fallbacks()`
- **Auto Rate-Limit Retry** — parses Groq's retry delay from 429 errors and waits exactly that long before retrying (up to 4 attempts), shows a toast notification
- **User Authentication** — Login / Register with SQLite + bcrypt password hashing; session-based auth with Sign Out
- **Professional Streamlit UI** — dark theme, real-time pipeline status cards, sidebar toggle, branded design
- **PDF Export** — download the full report as a formatted PDF (header, footer, page numbers) or Markdown
- **Docker Ready** — multi-stage Dockerfile with non-root user, health check, and compose file for one-command deploy
- **100% Free Stack** — Groq, Mistral, and Tavily all offer free tiers with no billing required
- **CLI Mode** — also runnable from terminal via `pipeline.py` for quick testing

---

## Tech Stack

| Layer | Technology | Free Tier |
|-------|-----------|-----------|
| UI | Streamlit 1.35+ | Yes |
| Auth | SQLite + bcrypt | Built-in |
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
├── app.py                  # Streamlit UI — auth gate, pipeline, results, PDF
├── auth.py                 # SQLite + bcrypt user registration and login
├── agents.py               # LLM setup (Groq + Mistral fallback), agent + chain definitions
├── pipeline.py             # 4-step CLI pipeline orchestrator
├── tools.py                # LangChain tools: web_search (Tavily), scrape_url (BS4)
├── main.py                 # CLI entry point (interactive + single-shot modes)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Single-command deployment
├── .dockerignore           # Excludes .venv, .env, .git from image
├── .streamlit/
│   └── config.toml         # Theme, server settings
└── .env                    # API keys — never committed (see Configuration)
```

---

## Prerequisites

- Python 3.10+
- Three free API keys (no billing required on any):

| Service | Get Key | Used For |
|---------|---------|---------|
| [Groq](https://console.groq.com/keys) | Free | Primary LLM |
| [Mistral](https://console.mistral.ai/) | Free | Fallback LLM |
| [Tavily](https://app.tavily.com/) | Free | Web Search |

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

**4. Configure API keys**

```env
# .env
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

You will be greeted with a **Login / Register** screen. Create an account, then enter any research topic and click **Run Research Pipeline**.

### CLI Mode (terminal)

```bash
python pipeline.py
```

```
Enter a research topic: machine learning in cybersecurity 2025
```

---

## Docker Deployment

**Build and run with Docker Compose:**

```bash
docker compose up --build
```

App will be available at **http://localhost:8501**

**Environment variables** are loaded from `.env` via the `env_file` directive in `docker-compose.yml`. The `users.db` SQLite database is persisted via a local `./data` volume mount.

**Single container run:**

```bash
docker build -t researchmind .
docker run -p 8501:8501 --env-file .env researchmind
```

---

## How the LLM Fallback Works

```
Every API call
     │
     ▼
 Groq — Llama 3.3 70B  ──── success ──► return result
     │
  rate limit / error
     │
     ▼
 Mistral — mistral-small  ──► return result
```

This is implemented using LangChain's built-in `with_fallbacks()` method — zero custom retry logic required at the chain level. Additionally, transient Groq 429 errors trigger an auto-wait (using the exact delay Groq reports in the error) before switching to Mistral.

---

## Pipeline Steps in Detail

### Step 1 — Search Agent
A **LangGraph ReAct agent** uses **Tavily** to fetch the 5 most relevant and recent web results for the topic. Returns titles, URLs, and content snippets.

### Step 2 — Reader Agent
A second **LangGraph ReAct agent** picks the most relevant URL from search results and uses **BeautifulSoup** to scrape and clean the full page text (up to 3,000 characters).

### Step 3 — Writer Chain
A **LangChain LCEL chain** combines search + scraped content and instructs the LLM to produce a full report:
- **Introduction**
- **Key Findings** — minimum 3 well-explained points with examples
- **Conclusion**
- **Sources** — all URLs referenced

### Step 4 — Critic Chain
A second **LCEL chain** acts as a research critic and returns:
- **Score** — X/10
- **Strengths** — what the report does well
- **Areas to Improve** — specific, actionable feedback
- **One-line verdict**

---

## Roadmap

- [x] 4-step multi-agent research pipeline
- [x] Groq free tier LLM backend (Llama 3.3 70B)
- [x] Mistral Small as automatic fallback (100% free)
- [x] Auto-retry with rate-limit delay parsing
- [x] Professional Streamlit UI with dark theme
- [x] Real-time pipeline step status cards
- [x] User authentication (register / login / logout)
- [x] PDF + Markdown report download
- [x] Docker multi-stage build + Compose deployment
- [ ] LangGraph state graph for parallel agent execution
- [ ] Multiple URL scraping per pipeline run
- [ ] Retry/refinement loop — if critic score < 7, re-run writer
- [ ] Research history per user (stored in SQLite)
- [ ] Streamlit Cloud one-click deploy

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change, then submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by **Aman Khan**

Powered by Groq · Mistral · LangChain · LangGraph · Tavily · Streamlit
