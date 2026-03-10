import pandas as pd
import io

def to_csv(df: pd.DataFrame) -> bytes:
    """Convert dataframe to CSV bytes for download."""
    output = io.BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def to_bibtex(df: pd.DataFrame) -> str:
    """Convert search results to a basic BibTeX format."""
    bib_entries = []
    for _, row in df.iterrows():
        # Sanitize title for key
        clean_title = "".join(filter(str.isalnum, row['title']))[:15]
        author_list = row['authors'].split(", ")
        first_author = author_list[0].split(" ")[-1] if author_list else "Unknown"
        key = f"{first_author}{row['year']}{clean_title}"
        
        entry = f"""@article{{{key},
  title = {{{row['title']}}},
  author = {{{row['authors']}}},
  year = {{{row['year']}}},
  note = {{Source: {row['source']}}},
  url = {{{row['url']}}}
}}"""
        bib_entries.append(entry)
    
    return "\n\n".join(bib_entries)
