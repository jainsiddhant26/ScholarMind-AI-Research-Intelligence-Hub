import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

from agents.search import get_combined_results
from agents.summarize import summarize_papers, detect_research_gaps
from agents.memory import save_search_to_memory, recall_memories
from utils.export import to_csv, to_bibtex

load_dotenv()

st.set_page_config(
    page_title="ScholarMind | AI Research Intelligence",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4F46E5;
        color: white;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 ScholarMind")
st.markdown("---")

if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "gaps" not in st.session_state:
    st.session_state.gaps = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "memory_saved_for" not in st.session_state:
    st.session_state.memory_saved_for = ""

with st.sidebar:
    st.header("📜 Research Memory")
    past_memories = recall_memories("")

    if past_memories:
        st.subheader("Related Past Interests")
        for mem in past_memories:
            content = mem.get("content", "")
            if content:
                st.caption(content[:120] + "...")
    else:
        st.caption("No past searches yet.")

    st.markdown("---")
    st.header("⚙️ Settings")

    api_status = "✅ Gemini Connected" if os.getenv("GEMINI_API_KEY") else "❌ Missing Gemini Key"
    st.info(api_status)

    db_status = "✅ Memory Active" if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY") else "⚠️ Memory Offline"
    st.info(db_status)

query = st.text_input(
    "Enter your research topic (e.g., 'Quantum Machine Learning in Drug Discovery')",
    placeholder="What are you curious about today?"
)

col1, col2 = st.columns([1, 4])
with col1:
    search_btn = st.button("Search Papers")

if search_btn and query:
    with st.spinner("🔍 Searching academic databases..."):
        df = get_combined_results(query)

        if not df.empty:
            summary = summarize_papers(df.to_dict("records"))
            gaps = detect_research_gaps(df.to_dict("records"))

            st.session_state.results_df = df
            st.session_state.summary = summary
            st.session_state.gaps = gaps
            st.session_state.last_query = query

            if st.session_state.memory_saved_for != query:
                saved = save_search_to_memory(query, summary)
                if saved:
                    st.session_state.memory_saved_for = query
        else:
            st.session_state.results_df = pd.DataFrame()
            st.session_state.summary = ""
            st.session_state.gaps = []
            st.session_state.last_query = query

if st.session_state.results_df is not None and not st.session_state.results_df.empty:
    df = st.session_state.results_df
    summary = st.session_state.summary
    gaps = st.session_state.gaps

    st.subheader("🤖 AI Intelligence Hub")
    summary_col, gap_col = st.columns([2, 1])

    with summary_col:
        st.markdown("### State of Research")
        st.write(summary)

    with gap_col:
        st.markdown("### 🕳️ Research Gaps")
        for gap in gaps:
            st.markdown(f"- {gap}")

    st.markdown("---")
    st.subheader("📊 Publication Trends")

    if "year" in df.columns:
        plot_df = df[df["year"] != "N/A"].copy()

        if not plot_df.empty:
            plot_df["year"] = plot_df["year"].astype(int)
            year_counts = plot_df["year"].value_counts().reset_index()
            year_counts.columns = ["Year", "Paper Count"]
            year_counts = year_counts.sort_values("Year")

            fig = px.line(
                year_counts,
                x="Year",
                y="Paper Count",
                markers=True,
                template="plotly_white",
                color_discrete_sequence=["#4F46E5"]
            )
            st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    st.subheader(f"📄 Search Results ({len(df)} papers found)")

    display_cols = [col for col in ["title", "authors", "year", "source", "url"] if col in df.columns]
    st.dataframe(
        df[display_cols],
        width="stretch",
        column_config={
            "url": st.column_config.LinkColumn("Link")
        } if "url" in df.columns else {}
    )

    st.markdown("### 📥 Export Tools")
    e_col1, e_col2 = st.columns(2)

    with e_col1:
        csv_data = to_csv(df)
        st.download_button(
            "Download CSV",
            csv_data,
            "scholarmind_results.csv",
            "text/csv"
        )

    with e_col2:
        bib_data = to_bibtex(df)
        st.download_button(
            "Download BibTeX",
            bib_data,
            "scholarmind_citations.bib",
            "text/plain"
        )

elif st.session_state.results_df is not None and st.session_state.results_df.empty:
    st.warning("No results found. Try a different query.")

else:
    st.info("👆 Enter a topic and hit Search to begin your scholarly journey.")

st.markdown("---")
st.caption("Built with ❤️ for the ScholarMind Portfolio Project.")
