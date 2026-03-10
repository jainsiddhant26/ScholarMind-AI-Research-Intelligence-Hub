import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def normalize_query(q: str) -> str:
    return " ".join(q.strip().lower().split())


def save_search_to_memory(query: str, summary: str) -> bool:
    if not supabase:
        print("Supabase not configured")
        return False

    normalized = normalize_query(query)

    try:
        data = {
            "user_id": "local_user",
            "query": query,
            "normalized_query": normalized,
            "content": f"Query: {query}\nSummary: {summary[:500]}"
        }

        supabase.table("research_memory").upsert(
            data,
            on_conflict="user_id,normalized_query"
        ).execute()

        print("Memory saved or updated successfully.")
        return True
    except Exception as e:
        print("Error saving memory:", e)
        return False


def recall_memories(query: str = ""):
    if not supabase:
        return []

    try:
        response = (
            supabase.table("research_memory")
            .select("*")
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print("Error recalling memories:", e)
        return []
