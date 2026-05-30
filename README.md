# Multi-Agent AI Research System

> An intelligent, multi-agent pipeline that autonomously searches the web, scrapes sources, writes structured research reports, and critiques them — all powered by Google Gemini and LangChain.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-green?logo=chainlink&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Pro-orange?logo=google&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Overview

The **Multi-Agent AI Research System** automates the full research lifecycle using a coordinated chain of specialized AI agents. Given any research topic, it:

1. **Searches** the web for recent, reliable information
2. **Scrapes** the most relevant web pages for deep content
3. **Writes** a professional, structured research report
4. **Critiques** the report for quality, accuracy, and completeness

Each stage is handled by a dedicated agent or LangChain Runnable, making the system modular, extensible, and transparent.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Research Pipeline                            │
│                                                                 │
│   User Input (Topic)                                            │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Search Agent │  ← Tavily Web Search API                     │
│  │  (Step 1)    │    Returns titles, URLs, snippets             │
│  └──────┬───────┘                                               │
│         │ search_results                                        │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Reader Agent │  ← BeautifulSoup Web Scraper                 │
│  │  (Step 2)    │    Picks top URL, extracts full text          │
│  └──────┬───────┘                                               │
│         │ scraped_content                                       │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Writer Chain │  ← Gemini 2.0 Pro LLM                        │
│  │  (Step 3)    │    Generates structured report                │
│  └──────┬───────┘                                               │
│         │ report                                                │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Critic Chain │  ← Gemini 2.0 Pro LLM                        │
│  │  (Step 4)    │    Scores & critiques the report              │
│  └──────┬───────┘                                               │
│         │ feedback                                              │
│         ▼                                                       │
│   Final Output (report + feedback dict)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

- **Autonomous Multi-Agent Pipeline** — four specialized agents work in sequence without manual intervention
- **Real-time Web Research** — Tavily search API provides fresh, reliable web results
- **Deep Content Extraction** — BeautifulSoup scraper pulls full page text beyond search snippets
- **Structured Report Generation** — LLM-driven writer produces reports with Introduction, Key Findings, Conclusion, and Sources
- **Automated Quality Review** — critic agent scores every report (X/10) with strengths and improvement areas
- **Rich Terminal Output** — color-formatted pipeline progress via the `rich` library
- **Dual Run Modes** — interactive CLI loop or single-shot command-line query

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM Backend | Google Gemini 2.0 Pro (`langchain-google-genai`) |
| Agent Framework | LangChain + LangGraph |
| Web Search | Tavily Search API (`tavily-python`) |
| Web Scraping | BeautifulSoup4 + Requests |
| Pipeline Orchestration | LangChain LCEL (Runnables) |
| Environment Config | python-dotenv |
| Terminal UI | Rich |

---

## Project Structure

```
Multi-Agent-AI-Research-System/
├── main.py            # CLI entry point (interactive + single-shot modes)
├── pipeline.py        # 4-step research pipeline orchestrator
├── agents.py          # Agent definitions: Search, Reader, Writer, Critic
├── tools.py           # LangChain tools: web_search (Tavily), scrape_url (BS4)
├── requirements.txt   # Python dependencies
└── .env               # API keys (not committed — see Configuration)
```

---

## Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key (Gemini)
- A [Tavily](https://tavily.com/) API key

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/Multi-Agent-AI-Research-System.git
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

**4. Configure API keys** — see [Configuration](#configuration) below

---

## Configuration

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> `.env` is listed in `.gitignore` and will never be committed.

---

## Usage

### Interactive Mode

Start an interactive research session where you can ask multiple questions:

```bash
python pipeline.py
```

```
Enter a research topic: artificial intelligence in healthcare
```

### Pipeline Output

The system prints live progress for each step:

```
 ================================================
step 1 - search agent is working ...
=================================================

 search result  [Tavily results...]

 ================================================
step 2 - Reader agent is scraping top resources ...
=================================================

 scraped content: [Full page text...]

 ================================================
step 3 - Writer is drafting the report ...
=================================================

 Final Report
 [Structured report with Introduction, Key Findings, Conclusion, Sources]

 ================================================
step 4 - critic is reviewing the report
=================================================

 critic report
 Score: 8/10

 Strengths:
 - ...

 Areas to Improve:
 - ...
```

---

## Pipeline Steps in Detail

### Step 1 — Search Agent
Uses the **Tavily Search API** to find the 5 most relevant and recent web results for the given topic. Returns titles, URLs, and content snippets.

### Step 2 — Reader Agent
Takes the search results, picks the most relevant URL, and uses **BeautifulSoup** to scrape the full page content (up to 3,000 characters of clean text).

### Step 3 — Writer Chain
Combines search snippets + scraped content and passes them to **Gemini 2.0 Pro** with a structured prompt. Outputs a full research report with:
- Introduction
- Key Findings (minimum 3 points)
- Conclusion
- Sources

### Step 4 — Critic Chain
Sends the report back to **Gemini 2.0 Pro** with a critic persona. Returns a structured review:
- Score (X/10)
- Strengths
- Areas to Improve
- One-line verdict

---

## Roadmap

- [ ] Fix `main.py` → wire it to `run_research_pipeline` in `pipeline.py`
- [ ] Add LangGraph state graph for true parallel agent execution
- [ ] Support multiple URL scraping (not just the top result)
- [ ] Add a retry/refinement loop — if critic score < 7, re-run the writer
- [ ] Export reports to Markdown or PDF
- [ ] Add a Streamlit or FastAPI web interface
- [ ] Add memory/context across multiple research sessions

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you'd like to change, then submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Built by **Aman Khan** — powered by Google Gemini, LangChain, and Tavily.
