"""Knowledge Explorer: Browse the complete forensic knowledge base."""

import streamlit as st
import re
from pathlib import Path

st.set_page_config(page_title="Knowledge Explorer", page_icon="📚", layout="wide")
st.title("Knowledge Explorer")
st.caption("Browse the complete forensic accounting knowledge base. Search red flags, techniques, and case studies.")

KB_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge_base"

# Load all knowledge base files
@st.cache_data
def load_kb_files():
    files = {}
    for f in sorted(KB_DIR.glob("*.md")):
        files[f.stem] = f.read_text(encoding="utf-8")
    return files

kb_files = load_kb_files()

# Sidebar navigation
with st.sidebar:
    st.subheader("Browse By Topic")
    topic_map = {
        "01_FRAMEWORK": "Forensic Framework",
        "02_RED_FLAGS_TAXONOMY": "Red Flags (74)",
        "03_GREEN_FLAGS": "Green Flags",
        "04_COMPANY_CASE_STUDIES": "Company Case Studies",
        "05_CHECKLIST": "Analysis Checklist",
        "06_PROMPT_TEMPLATES": "Prompt Templates",
        "07_MANIPULATION_TECHNIQUES": "Manipulation Techniques",
        "08_LLM_TRAINING_GUIDE": "LLM Training Guide",
        "09_ADDITIONAL_USE_CASES": "Additional Use Cases",
        "10_KEY_CONCEPTS_GLOSSARY": "Glossary & Concepts",
    }
    selected = st.radio(
        "Select topic:",
        list(topic_map.keys()),
        format_func=lambda x: topic_map.get(x, x),
    )

    st.divider()

    # Global search
    st.subheader("Search All Documents")
    search_query = st.text_input("Search term", placeholder="e.g., SSGR, pledge, Omkar")

# Main content
if search_query:
    st.subheader(f"Search Results for: '{search_query}'")
    total_results = 0
    for filename, content in kb_files.items():
        matches = list(re.finditer(re.escape(search_query), content, re.IGNORECASE))
        if matches:
            label = topic_map.get(filename, filename)
            with st.expander(f"**{label}** ({len(matches)} matches)", expanded=(total_results < 3)):
                for i, m in enumerate(matches[:10]):
                    start = max(0, m.start() - 200)
                    end = min(len(content), m.end() + 200)
                    context = content[start:end].replace("\n", " ")
                    st.markdown(f"{i+1}. ...{context}...")
                    st.divider()
                if len(matches) > 10:
                    st.caption(f"+{len(matches) - 10} more matches")
            total_results += len(matches)

    if total_results == 0:
        st.info(f"No results found for '{search_query}'. Try a different term.")
    else:
        st.success(f"Found {total_results} total matches across {sum(1 for f, c in kb_files.items() if search_query.lower() in c.lower())} documents")

else:
    # Display selected document
    if selected in kb_files:
        content = kb_files[selected]
        label = topic_map.get(selected, selected)
        st.subheader(label)

        # Render markdown
        st.markdown(content)

        # Download
        st.download_button(
            f"Download {label}",
            content,
            f"{selected}.md",
            "text/markdown",
        )
    else:
        st.error(f"File not found: {selected}")

# Quick stats
with st.sidebar:
    st.divider()
    st.subheader("Knowledge Base Stats")
    total_chars = sum(len(c) for c in kb_files.values())
    st.metric("Documents", len(kb_files))
    st.metric("Total Content", f"{total_chars:,} chars")
    st.metric("Approx. Pages", f"{total_chars // 3000}")
