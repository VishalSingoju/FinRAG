import os
import tempfile

import streamlit as st

from rag_engine import (
    index_pdf,
    retrieve_context,
    generate_answer,
    create_gemini_client,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Statement Analyst",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Financial Statement Analyst")

st.markdown(
    """
    **Analyze company annual reports using Retrieval-Augmented Generation.**

    Upload an annual report PDF, index it, and ask questions
    about financial statements, revenue, profit, assets,
    liabilities, cash flow, and other reported information.
    """
)


st.info(
    "Educational/research tool only. "
    "Always verify important figures against the original annual report."
)


# ============================================================
# GEMINI CLIENT
# ============================================================

try:

    gemini_client = create_gemini_client()

except Exception as error:

    st.error(
        f"Gemini configuration error: {error}"
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "collection_name" not in st.session_state:

    st.session_state.collection_name = None


if "pdf_name" not in st.session_state:

    st.session_state.pdf_name = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📄 Upload Report")

    uploaded_file = st.file_uploader(
        "Upload an annual report PDF",
        type=["pdf"]
    )

    st.markdown("---")

    st.caption(
        "Your PDF is processed into text chunks, "
        "embedded locally, and stored in ChromaDB."
    )


# ============================================================
# PDF PROCESSING
# ============================================================

if uploaded_file is not None:

    st.subheader(
        f"📄 {uploaded_file.name}"
    )

    if st.button(
        "🔍 Process & Index PDF",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Extracting, chunking, embedding, and indexing PDF..."
        ):

            try:

                # Create temporary PDF file
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temporary_file:

                    temporary_file.write(
                        uploaded_file.getbuffer()
                    )

                    temporary_pdf_path = (
                        temporary_file.name
                    )

                # Index PDF
                collection_name = index_pdf(
                    temporary_pdf_path
                )

                # Store in session
                st.session_state.collection_name = (
                    collection_name
                )

                st.session_state.pdf_name = (
                    uploaded_file.name
                )

                # Remove temporary file
                try:
                    os.remove(
                        temporary_pdf_path
                    )
                except Exception:
                    pass

                st.success(
                    "PDF successfully indexed! "
                    "You can now ask questions."
                )

            except Exception as error:

                st.error(
                    f"Failed to process PDF: {error}"
                )


# ============================================================
# CHECK WHETHER A PDF IS READY
# ============================================================

if st.session_state.collection_name:

    st.success(
        f"Ready to analyze: "
        f"**{st.session_state.pdf_name}**"
    )

    st.markdown("---")

    # ========================================================
    # QUESTION INPUT
    # ========================================================

    st.subheader("💬 Ask a Question")

    question = st.text_area(
        "What would you like to know?",
        placeholder=(
            "Example: What was the company's revenue "
            "in FY2025 compared with FY2024?"
        ),
        height=100
    )

    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    if st.button(
        "🤖 Analyze",
        type="primary",
        use_container_width=True
    ):

        if not question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            # ================================================
            # RETRIEVAL
            # ================================================

            with st.spinner(
                "Searching the annual report..."
            ):

                try:

                    retrieved_chunks = retrieve_context(
                        st.session_state.collection_name,
                        question,
                        top_k=5
                    )

                except Exception as error:

                    st.error(
                        f"Retrieval failed: {error}"
                    )

                    st.stop()

            if not retrieved_chunks:

                st.warning(
                    "I couldn't find relevant information "
                    "in the uploaded report."
                )

            else:

                # ============================================
                # GENERATION
                # ============================================

                with st.spinner(
                    "Analyzing the financial information..."
                ):

                    try:

                        answer = generate_answer(
                            gemini_client,
                            question,
                            retrieved_chunks
                        )

                    except Exception as error:

                        st.error(
                            f"Gemini generation failed: {error}"
                        )

                        st.stop()

                # ============================================
                # ANSWER
                # ============================================

                st.subheader("📈 Answer")

                st.markdown(answer)

                # ============================================
                # SOURCES
                # ============================================

                st.markdown("---")

                st.subheader(
                    "📚 Retrieved Sources"
                )

                for index, chunk in enumerate(
                    retrieved_chunks,
                    start=1
                ):

                    with st.expander(
                        f"Source {index} • PDF Page {chunk['page']}"
                    ):

                        st.write(
                            chunk["text"]
                        )

else:

    # ========================================================
    # INITIAL STATE
    # ========================================================

    st.markdown(
        """
        ### 🚀 How it works

        1. **Upload** a company annual report.
        2. **Process & Index** the PDF.
        3. **Ask** a financial question.
        4. The app retrieves the most relevant sections.
        5. **Gemini** analyzes only those retrieved sections.
        6. The app shows the **source PDF pages** used.

        This is a basic RAG pipeline:

        **PDF → Text → Chunks → Embeddings → ChromaDB → Retrieval → Gemini → Answer**
        """
    )