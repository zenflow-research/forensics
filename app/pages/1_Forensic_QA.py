"""Forensic Q&A: RAG-powered question answering over the knowledge base."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.rag_engine import RAGEngine

st.set_page_config(page_title="Forensic Q&A", page_icon="🔍", layout="wide")
st.title("Forensic Q&A Engine")
st.caption("Ask any question about forensic accounting. Powered by semantic search over Dr. Malik's complete knowledge base.")

# Initialize RAG
@st.cache_resource
def get_rag():
    engine = RAGEngine()
    return engine

rag = get_rag()

# Index status
with st.sidebar:
    st.subheader("Knowledge Base Status")
    try:
        rag.initialize()
        count = rag.collection.count()
        st.metric("Indexed Chunks", count)
        if count == 0:
            if st.button("Index Knowledge Base", type="primary"):
                with st.spinner("Indexing documents..."):
                    n = rag.index_knowledge_base(force=True)
                st.success(f"Indexed {n} chunks!")
                st.rerun()
        else:
            if st.button("Re-index (Force)"):
                with st.spinner("Re-indexing..."):
                    n = rag.index_knowledge_base(force=True)
                st.success(f"Re-indexed {n} chunks!")
                st.rerun()
    except Exception as e:
        st.error(f"RAG init error: {e}")
        count = 0

    st.divider()
    n_results = st.slider("Results to retrieve", 3, 15, 8)

    st.divider()
    st.subheader("Sample Questions")
    sample_questions = [
        "What is SSGR and how to calculate it?",
        "How to detect if dividends are funded by debt?",
        "What are the red flags in related party transactions?",
        "What is the Trinity pattern?",
        "How did Omkar Speciality manipulate accounts?",
        "What is credit rating shopping?",
        "Red flags specific to pharma companies?",
        "What is the vicious cycle of promoter remuneration?",
        "How to analyze cash flow statement forensically?",
        "What are green flags in management quality?",
    ]
    for q in sample_questions:
        if st.button(q, key=f"sq_{q[:20]}", use_container_width=True):
            st.session_state["qa_input"] = q

# Main Q&A
question = st.text_input(
    "Ask a forensic accounting question:",
    value=st.session_state.get("qa_input", ""),
    placeholder="e.g., How to detect if a company is paying dividends from borrowed money?",
)

if question and count > 0:
    with st.spinner("Searching knowledge base..."):
        results = rag.query(question, n_results=n_results)

    if results:
        st.subheader("Relevant Knowledge")

        # Build combined context for display
        for i, r in enumerate(results):
            relevance_color = "green" if r["relevance"] > 0.5 else "orange" if r["relevance"] > 0.3 else "red"
            with st.expander(
                f"**{r['source']}** | Relevance: :{relevance_color}[{r['relevance']:.0%}]",
                expanded=(i < 3),
            ):
                st.markdown(r["text"])

        st.divider()

        # Generate prompt for LLM
        st.subheader("Ready-to-Use LLM Prompt")
        context = rag.get_context_for_prompt(question, n_results)
        prompt = f"""You are an expert forensic accountant trained in Dr. Vijay Malik's "Peaceful Investing" methodology.

Based on the following knowledge base context, answer the user's question thoroughly with specific examples and data.

CONTEXT:
{context}

QUESTION: {question}

Provide a comprehensive answer with:
1. Clear explanation of the concept
2. How to detect/calculate it
3. Real company examples where applicable
4. Severity assessment and what action to take
"""
        st.code(prompt, language="text")
        st.download_button(
            "Download Prompt",
            prompt,
            file_name="forensic_prompt.txt",
            mime="text/plain",
        )
    else:
        st.warning("No relevant results found. Try rephrasing your question.")

elif question and count == 0:
    st.warning("Knowledge base not indexed yet. Click 'Index Knowledge Base' in the sidebar.")

# Chat history
if "qa_history" not in st.session_state:
    st.session_state["qa_history"] = []

if question and question not in [h["q"] for h in st.session_state["qa_history"]]:
    st.session_state["qa_history"].append({"q": question, "n": len(results) if 'results' in dir() else 0})

if st.session_state["qa_history"]:
    with st.sidebar:
        st.divider()
        st.subheader("Search History")
        for h in reversed(st.session_state["qa_history"][-10:]):
            st.caption(f"Q: {h['q'][:50]}...")
