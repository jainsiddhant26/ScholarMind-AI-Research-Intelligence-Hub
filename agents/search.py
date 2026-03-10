import requests
import pandas as pd
import time
import random
import xml.etree.ElementTree as ET
from typing import List, Dict


def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            link = entry.find("atom:id", ns)
            authors = entry.findall("atom:author", ns)

            results.append({
                "title": title.text.strip() if title is not None else "N/A",
                "authors": ", ".join([
                    a.find("atom:name", ns).text
                    for a in authors
                    if a.find("atom:name", ns) is not None
                ]),
                "abstract": summary.text.strip() if summary is not None else "No abstract available.",
                "year": published.text[:4] if published is not None else "N/A",
                "url": link.text.strip() if link is not None else "N/A",
                "source": "ArXiv"
            })

        return results

    except Exception as e:
        print(f"Error searching ArXiv: {e}")
        return []


def search_semantic_scholar(query: str, limit: int = 2) -> List[Dict]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,abstract,year,url"
    }

    headers = {
        "User-Agent": "ScholarMind/1.0"
    }

    for attempt in range(4):
        try:
            time.sleep(2.5)
            response = requests.get(url, params=params, headers=headers, timeout=20)

            if response.status_code == 429:
                wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                print(f"Semantic Scholar rate limit hit. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()

            results = []
            for paper in data.get("data", []):
                results.append({
                    "title": paper.get("title", "N/A"),
                    "authors": ", ".join([
                        a.get("name", "Unknown")
                        for a in paper.get("authors", [])
                    ]),
                    "abstract": paper.get("abstract", "No abstract available."),
                    "year": paper.get("year", "N/A"),
                    "url": paper.get("url", "N/A"),
                    "source": "Semantic Scholar"
                })

            return results

        except requests.RequestException as e:
            if attempt == 3:
                print(f"Error searching Semantic Scholar: {e}")
                return []

    return []


def get_combined_results(query: str, limit_per_source: int = 5) -> pd.DataFrame:
    arxiv_res = search_arxiv(query, max_results=limit_per_source)
    ss_res = search_semantic_scholar(query, limit=2)

    all_res = arxiv_res + ss_res
    df = pd.DataFrame(all_res)

    if not df.empty:
        df["title_lower"] = df["title"].astype(str).str.lower().str.strip()
        df = df.drop_duplicates(subset=["title_lower"]).drop(columns=["title_lower"])
        df = df.reset_index(drop=True)

    return df
