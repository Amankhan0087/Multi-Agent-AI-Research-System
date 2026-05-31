from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from tools import web_search, scrape_url
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

_key = os.getenv("GROQ_API_KEY")

# Agents use fewer tokens — they only call tools and give brief summaries
llm_agent = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=_key,
    temperature=0,
    max_tokens=700,
)

# Writer and critic chains need more room for full reports
llm_chain = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=_key,
    temperature=0,
    max_tokens=1500,
)


#1st agent
def build_search_agent():
    return create_react_agent(llm_agent, [web_search])


#2nd agent
def build_reader_agent():
    return create_react_agent(llm_agent, [scrape_url])


#Writer chain 

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


#critic_chain

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


