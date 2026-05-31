from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import web_search, scrape_url
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()


def _build_llm(max_tokens_groq: int, max_tokens_gemini: int):
    """
    Build an LLM with Gemini as automatic fallback when Groq hits rate limits.
    If GEMINI_API_KEY is not set, returns Groq only.
    """
    groq = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=max_tokens_groq,
    )

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return groq  # no fallback configured

    gemini = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_key,
        temperature=0,
        max_output_tokens=max_tokens_gemini,
    )

    # Groq first → Gemini on any failure (rate limit, quota, downtime)
    return groq.with_fallbacks([gemini])


# Agents: brief tool calls + short summaries
llm_agent = _build_llm(max_tokens_groq=700, max_tokens_gemini=800)

# Writer & Critic: full report generation
llm_chain = _build_llm(max_tokens_groq=1500, max_tokens_gemini=1800)


# 1st agent
def build_search_agent():
    return create_react_agent(llm_agent, [web_search])


# 2nd agent
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
