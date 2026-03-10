import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_papers(papers):
    client = get_client()
    context = "\n\n".join([
        "Title: " + str(p.get('title','')) + "\nAbstract: " + str(p.get('abstract',''))
        for p in papers[:5]
    ])
    prompt = "Summarize these research papers in 2-3 paragraphs:\n\n" + context + "\n\nSummary:"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Summary error: " + str(e)[:200]

def detect_research_gaps(papers):
    client = get_client()
    context = "\n\n".join([
        "Title: " + str(p.get('title','')) + "\nAbstract: " + str(p.get('abstract',''))
        for p in papers[:5]
    ])
    prompt = "List exactly 3 research gaps from these papers as bullet points:\n\n" + context + "\n\nResearch Gaps:"
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        gaps = response.choices[0].message.content.strip().split("\n")
        clean_gaps = [g.strip("- ").strip("* ").strip() for g in gaps if g.strip()]
        return clean_gaps[:3] if clean_gaps else ["No gaps identified."]
    except Exception as e:
        return ["Gap error: " + str(e)[:200]]
