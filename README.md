# 📊 Financial Statement RAG Analyst

A simple RAG-based application for asking questions about company annual reports.

Upload an annual report PDF, process it, and ask questions like:

- What was the revenue in FY2025?
- What was the net profit?
- How did revenue change compared to the previous year?
- What were the total assets?
- What was the operating cash flow?

The application searches the uploaded report and sends the most relevant sections to Gemini to generate the answer.

> **Note:** This is an educational/research project. Always verify financial information with the original annual report.

---

## Why I built this

Annual reports can be hundreds of pages long. Finding one specific number or piece of information manually can take a lot of time.

I wanted to build a small project that combines **AI + Finance** and use RAG to make these reports easier to search.

The main idea is:

```text
Annual Report PDF
       ↓
Extract Text
       ↓
Split into Chunks
       ↓
Create Embeddings
       ↓
Store in ChromaDB
       ↓
Search Relevant Chunks
       ↓
Send Context to Gemini
       ↓
Answer + Source Pages
```

---

## How it works

The project has two main parts.

### 1. Document processing

When a PDF is uploaded:

```text
PDF
 ↓
PyMuPDF
 ↓
Text extraction
 ↓
Text chunking
 ↓
Sentence Transformer
 ↓
Embeddings
 ↓
ChromaDB
```

The PDF is split into smaller chunks and converted into embeddings using:

`sentence-transformers/all-MiniLM-L6-v2`

These embeddings are stored in ChromaDB along with the PDF page number.

### 2. Question answering

When a question is asked:

```text
Question
   ↓
Question Embedding
   ↓
ChromaDB Similarity Search
   ↓
Top 5 Relevant Chunks
   ↓
Gemini
   ↓
Answer
```

The retrieved chunks are included in the prompt sent to Gemini.

The model is instructed to use the provided report information and avoid making up financial figures.

---

## Architecture

```text
                 User
                  │
                  ▼
            ┌───────────┐
            │ Streamlit │
            └─────┬─────┘
                  │
          Upload Annual Report
                  │
                  ▼
             ┌─────────┐
             │ PyMuPDF │
             └────┬────┘
                  │
                  ▼
           Text Chunking
                  │
                  ▼
        ┌──────────────────┐
        │ Sentence         │
        │ Transformers     │
        └────────┬─────────┘
                 │
                 ▼
            ┌──────────┐
            │ ChromaDB │
            └────┬─────┘
                 │
           Semantic Search
                 │
                 ▼
          Relevant Chunks
                 │
                 ▼
            ┌─────────┐
            │ Gemini  │
            └────┬────┘
                 │
                 ▼
          Answer + Sources
```

---

## Tech Stack

| Technology | Used for |
|---|---|
| Python | Main programming language |
| Streamlit | Web application |
| PyMuPDF | PDF text extraction |
| LangChain Text Splitters | Text chunking |
| Sentence Transformers | Text embeddings |
| ChromaDB | Vector database |
| Google Gemini | Answer generation |
| python-dotenv | Environment variables |
| Docker | Containerization |
| GitHub | Version control |
| Streamlit Community Cloud | Deployment |

---

## Project Structure

```text
financial-statement-rag/
│
├── app.py
├── rag_engine.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── README.md
│
└── .streamlit/
    └── config.toml
```

### `app.py`

Contains the Streamlit UI.

It handles:

- PDF upload
- Processing button
- Question input
- Showing answers
- Showing retrieved sources

### `rag_engine.py`

Contains the main RAG logic:

- PDF extraction
- Text chunking
- Embeddings
- ChromaDB
- Retrieval
- Gemini API
- Prompt construction

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-statement-rag.git

cd financial-statement-rag
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Gemini API key

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
```

Do not commit this file to GitHub.

### 5. Run

```bash
streamlit run app.py
```

---

## Docker

The project also includes a Dockerfile.

Build the image:

```bash
docker build -t financial-statement-rag .
```

Run it:

```bash
docker run -p 7860:7860 financial-statement-rag
```

Then open:

```text
http://localhost:7860
```

---

## Deployment

The application can be deployed using **Streamlit Community Cloud**.

Basic deployment flow:

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
Streamlit App
       ↓
Gemini API
```

The Gemini API key is added through Streamlit Secrets instead of being stored in the GitHub repository.

Example secret:

```toml
GEMINI_API_KEY = "your_api_key"
```

---

## Example

Upload an annual report and ask:

```text
What was the company's revenue in FY2025?
```

The application:

1. Converts the question into an embedding.
2. Searches ChromaDB.
3. Retrieves the most relevant report sections.
4. Sends those sections to Gemini.
5. Generates the answer.
6. Shows the PDF pages used as sources.

---

## Current Limitations

This is currently a small project, so there are some limitations:

- Complex PDF tables may not extract perfectly.
- Scanned PDFs may require OCR.
- Retrieval quality depends on the generated embeddings.
- ChromaDB is currently used as local storage.
- The application currently focuses on one uploaded report at a time.
- Generated answers should still be checked against the original report.

---

## Things I want to improve

Some things I would like to add later:

- [ ] Multiple PDF support
- [ ] Compare two companies
- [ ] Financial ratio calculations
- [ ] Charts for revenue/profit trends
- [ ] Better table extraction
- [ ] OCR for scanned reports
- [ ] Hybrid search
- [ ] Reranking
- [ ] Remote vector database
- [ ] RAG evaluation
- [ ] Better monitoring

---

---

## Author

**Vishal Singoju**

B.Tech Graduate | AI/ML | FinTech

GitHub: `https://github.com/VishalSingoju`
