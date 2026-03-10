import arxiv
import requests
import pandas as pd
import time
import random
from typing import List, Dict


def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for res in search.results():
            results.append({
                "title": res.title,
                "authors": ", ".join([a.name for a in res.authors]),
                "abstract": res.summary,
                "year": res.published.year,
                "url": res.entry_id,
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
                    "authors": ", ".join([a.get("name", "Unknown") for a in paper.get("authors", [])]),
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
