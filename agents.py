from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from tools import web_search, scrape_url
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()


def _get_key(name: str) -> str:
    """Read API key from env (.env locally) or Streamlit Cloud secrets."""
    val = os.getenv(name, "")
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(name, "")
        except Exception:
            pass
    return val


def _build_llm(max_tokens_groq: int, max_tokens_mistral: int):
    """
    Primary : Groq — Llama 3.3 70B Versatile  (12,000 TPM free tier)
    Fallback : Mistral — mistral-small-latest  (1B tokens/month free tier)

    LangChain automatically switches to Mistral on any Groq failure
    (rate limit, quota, downtime) without any extra code.
    If MISTRAL_API_KEY is not set, falls back to Groq-only mode.
    """
    groq = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=_get_key("GROQ_API_KEY"),
        temperature=0,
        max_tokens=max_tokens_groq,
    )

    mistral_key = _get_key("MISTRAL_API_KEY")
    if not mistral_key:
        return groq

    mistral = ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=mistral_key,
        temperature=0,
        max_tokens=max_tokens_mistral,
    )

    # Groq first → Mistral on any failure
    return groq.with_fallbacks([mistral])


# Agents: tool calls + brief summaries (low token budget)
llm_agent = _build_llm(max_tokens_groq=700, max_tokens_mistral=800)

# Writer & Critic: full report generation (higher token budget)
llm_chain = _build_llm(max_tokens_groq=1500, max_tokens_mistral=1800)


# 1st agent — web search
def build_search_agent():
    return create_react_agent(llm_agent, [web_search])


# 2nd agent — web scraper
def build_reader_agent():
    return create_react_agent(llm_agent, [scrape_url])


# Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm_chain | StrOutputParser()


# Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm_chain | StrOutputParser()
