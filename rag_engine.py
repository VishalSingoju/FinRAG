import os
import time
import hashlib

import chromadb
import pymupdf

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv(override=True)

DB_PATH = "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Primary Gemini model
GEMINI_MODEL = "gemini-3.5-flash-lite"

# Fallback model if the primary model is temporarily unavailable
GEMINI_FALLBACK_MODEL = "gemini-3.1-flash-lite"

TOP_K = 5


# ============================================================
# INITIALIZE EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(EMBEDDING_MODEL)


# ============================================================
# INITIALIZE CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=DB_PATH
)


# ============================================================
# GEMINI CLIENT
# ============================================================

def create_gemini_client():
    """
    Create and return a Gemini API client.

    The API key can come from:
    - local .env file
    - Streamlit Cloud Secrets
    - environment variables
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file or deployment secrets."
        )

    return genai.Client(api_key=api_key)


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(pdf_path):
    """
    Extract text from every page of the PDF.

    Returns:
        List of dictionaries containing:
        - page
        - text
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        if text and text.strip():

            pages.append(
                {
                    "page": page_number,
                    "text": text.strip()
                }
            )

    document.close()

    return pages


# ============================================================
# TEXT CHUNKING
# ============================================================

def create_chunks(pages):
    """
    Split PDF text into smaller chunks while keeping
    the original PDF page number.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for page_data in pages:

        page_number = page_data["page"]
        page_text = page_data["text"]

        split_texts = text_splitter.split_text(page_text)

        for chunk in split_texts:

            chunks.append(
                {
                    "text": chunk,
                    "page": page_number
                }
            )

    return chunks


# ============================================================
# COLLECTION NAME
# ============================================================

def get_collection_name(pdf_path):
    """
    Create a stable ChromaDB collection name based on
    the PDF filename.
    """

    filename = os.path.basename(pdf_path)

    file_hash = hashlib.md5(
        filename.encode("utf-8")
    ).hexdigest()[:10]

    safe_name = (
        "".join(
            character
            if character.isalnum()
            else "_"
            for character in os.path.splitext(filename)[0]
        )
        .lower()
    )

    return f"financial_report_{safe_name}_{file_hash}"


# ============================================================
# INDEX PDF
# ============================================================

def index_pdf(pdf_path):
    """
    Extract, chunk, embed, and store a PDF in ChromaDB.

    Returns:
        collection_name
    """

    pages = extract_pdf_text(pdf_path)

    if not pages:
        raise ValueError(
            "No readable text was found in the PDF."
        )

    chunks = create_chunks(pages)

    if not chunks:
        raise ValueError(
            "The PDF could not be split into text chunks."
        )

    collection_name = get_collection_name(pdf_path)

    # Delete old collection if it already exists
    try:
        chroma_client.delete_collection(
            name=collection_name
        )
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=collection_name
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=False
    ).tolist()

    ids = [
        f"chunk_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "page": chunk["page"],
            "chunk_index": index
        }
        for index, chunk in enumerate(chunks)
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return collection_name


# ============================================================
# RETRIEVE RELEVANT CONTEXT
# ============================================================

def retrieve_context(collection_name, question, top_k=TOP_K):
    """
    Convert the user's question into an embedding and
    retrieve the most relevant chunks from ChromaDB.
    """

    collection = chroma_client.get_collection(
        name=collection_name
    )

    question_embedding = embedding_model.encode(
        [question]
    ).tolist()

    results = collection.query(
        query_embeddings=question_embedding,
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    retrieved_chunks = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        retrieved_chunks.append(
            {
                "text": document,
                "page": metadata.get("page", "Unknown")
            }
        )

    return retrieved_chunks


# ============================================================
# BUILD PROMPT
# ============================================================

def build_financial_prompt(
    question,
    retrieved_chunks
):
    """
    Build a grounded financial-analysis prompt.
    """

    context_parts = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {index}

PDF PAGE:
{chunk["page"]}

CONTENT:
{chunk["text"]}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a careful financial statement analysis assistant.

Your job is to answer questions using ONLY the
provided annual-report excerpts.

IMPORTANT RULES:

1. Do not invent financial figures.
2. Do not use outside information.
3. If the answer cannot be found in the provided excerpts,
   clearly say that the information is not available.
4. Preserve the original currency.
5. Preserve financial years correctly.
6. Distinguish between reported figures and your own calculations.
7. If you calculate a percentage change, show the calculation.
8. Mention the relevant PDF page number when possible.
9. Do not provide personalized investment advice.
10. Do not make assumptions about missing numbers.
11. Keep the answer concise but useful.
12. When comparing years, clearly label each year.
13. If multiple sources support the answer, mention all
    relevant page numbers.

ANNUAL REPORT EXCERPTS:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    return prompt


# ============================================================
# GEMINI GENERATION
# ============================================================

def _generate_with_model(
    client,
    model,
    prompt
):
    """
    Send the prompt to Gemini.
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text


# ============================================================
# GENERATE ANSWER WITH FALLBACK
# ============================================================

def generate_answer(
    client,
    question,
    retrieved_chunks
):
    """
    Generate an answer using Gemini.

    Primary:
        gemini-3.5-flash-lite

    Fallback:
        gemini-3.1-flash-lite

    Temporary server errors are retried.
    """

    if not retrieved_chunks:
        return (
            "I couldn't find relevant information "
            "in the uploaded annual report."
        )

    prompt = build_financial_prompt(
        question,
        retrieved_chunks
    )

    models = [
        GEMINI_MODEL,
        GEMINI_FALLBACK_MODEL
    ]

    last_error = None

    for model in models:

        # Retry temporary server problems
        for attempt in range(2):

            try:

                return _generate_with_model(
                    client,
                    model,
                    prompt
                )

            except Exception as error:

                last_error = error

                error_text = str(error)

                # Retry only likely temporary server problems
                is_temporary = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "temporarily" in error_text.lower()
                    or "high demand" in error_text.lower()
                )

                if not is_temporary:
                    raise

                # Small exponential backoff
                wait_time = 2 ** attempt

                time.sleep(wait_time)

        # Try fallback model after primary failure

    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        "Please try again in a moment."
    ) from last_error