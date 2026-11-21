from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

pool = []

# max_retries=0 ensures instant fallback instead of 30-60s rate-limit sleep
if groq_api_key:
    groq_fast = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=groq_api_key,
        temperature=0,
        timeout=25,
        max_retries=0,
    )
    groq_smart = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=groq_api_key,
        temperature=0,
        timeout=35,
        max_retries=0,
    )
    groq_qwen = ChatGroq(
        model="qwen/qwen3.8-27b",
        api_key=groq_api_key,
        temperature=0,
        timeout=25,
        max_retries=0,
    )
    pool.extend([groq_fast, groq_smart, groq_qwen])

if google_api_key:
    gemini_lite = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=google_api_key,
        timeout=30,
        max_retries=0,
    )
    pool.append(gemini_lite)

if not pool:
    raise ValueError("Add at least GROQ_API_KEY or GOOGLE_API_KEY in your .env file")


def make_agent(primary, tools):
    fallbacks = [m for m in pool if m is not primary]
    mw = [ModelFallbackMiddleware(*fallbacks)] if fallbacks else []
    return create_agent(model=primary, tools=tools, middleware=mw)


# Step 1 uses gpt-oss-20b (own 8K TPM bucket, ~1000 tok/s)
def build_search_agent():
    primary = pool[0]
    return make_agent(primary, [web_search])


# Step 2 uses Gemini Lite or Qwen (fresh bucket — zero 429 wait after Step 1!)
def build_reader_agent():
    primary = pool[-1] if len(pool) > 1 else pool[0]
    return make_agent(primary, [scrape_url])


# Step 3 & 4 use gpt-oss-120b (its own fresh 8K TPM bucket)
writer_primary = pool[1] if len(pool) > 1 else pool[0]
writer_fallbacks = [m for m in pool if m is not writer_primary]
chain_llm = writer_primary.with_fallbacks(writer_fallbacks) if writer_fallbacks else writer_primary

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
writer_chain = writer_prompt | chain_llm | StrOutputParser()

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
critic_chain = critic_prompt | chain_llm | StrOutputParser()