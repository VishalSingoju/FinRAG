# 📊 Financial Statement RAG Analyst

An AI-powered **Retrieval-Augmented Generation (RAG)** application that analyzes company annual reports and financial statements using **document retrieval, semantic search, vector databases, and Google Gemini**.

The application allows users to upload an annual-report PDF, index its contents, and ask natural-language questions about financial performance, revenue, profit, assets, liabilities, cash flow, and other information contained in the report.

Instead of sending the entire document directly to an LLM, the system retrieves the most relevant sections from the report and provides them to the language model as context. This improves grounding and allows answers to be traced back to the relevant PDF pages.

> **Educational and research project.** Financial information and generated answers should always be verified against the original annual report. This application does not provide personalized investment advice.

---

## 🚀 Project Overview

Financial annual reports can contain hundreds of pages of financial statements, management discussions, notes, accounting information, tables, and other disclosures.

Finding a specific piece of information manually can be time-consuming.

This project addresses that problem by building a **document question-answering system for financial reports**.

A user can upload an annual report and ask questions such as:

```text
What was the company's revenue in FY2025?

How did net profit change compared with FY2024?

What were the company's total assets?

What was the operating cash flow?

What caused the change in revenue?

What were the major liabilities reported by the company?
```

The system retrieves the most relevant sections of the report and uses Gemini to generate a concise answer based only on the retrieved information.

---

# 🎯 Why This Project Is Needed

Annual reports contain valuable financial information, but extracting specific information manually has several challenges:

- Reports can contain hundreds of pages.
- Financial information is distributed across multiple sections.
- The same metric may appear in different parts of the document.
- Users may need to compare multiple financial years.
- Traditional keyword search may miss semantically related information.
- Large documents cannot always be efficiently passed directly to an LLM.

A RAG-based system provides a more practical approach:

```text
Annual Report
      ↓
Extract relevant text
      ↓
Split into smaller chunks
      ↓
Convert chunks into embeddings
      ↓
Store embeddings in vector database
      ↓
Search for semantically relevant chunks
      ↓
Send retrieved context to LLM
      ↓
Generate grounded answer
      ↓
Show source PDF pages
```

The main objective is to combine **financial-document analysis with modern AI retrieval techniques** while reducing the risk of unsupported or hallucinated answers.

---

# 🧠 What Is RAG?

**Retrieval-Augmented Generation (RAG)** combines information retrieval with a Large Language Model.

Instead of asking an LLM to answer using only its pretrained knowledge, the system first retrieves relevant information from a private knowledge source.

In this project:

```text
User Question
      │
      ▼
Question Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Relevant Annual Report Chunks
      │
      ▼
Gemini
      │
      ▼
Grounded Financial Answer
```

This allows the model to answer questions using information from the uploaded annual report rather than relying solely on general model knowledge.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │       User           │
                         │                      │
                         │ Upload PDF + Question│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Streamlit       │
                         │     Web Interface    │
                         └──────────┬───────────┘
                                    │
                         PDF Upload │
                                    ▼
                         ┌──────────────────────┐
                         │       PyMuPDF        │
                         │    PDF Extraction    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Recursive Character │
                         │    Text Splitter     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Sentence Transformers│
                         │   all-MiniLM-L6-v2   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      ChromaDB        │
                         │    Vector Storage    │
                         └──────────┬───────────┘
                                    │
                              Semantic Search
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Relevant PDF Chunks  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Google Gemini     │
                         │       LLM            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Grounded Answer +    │
                         │ Source PDF Pages     │
                         └──────────────────────┘
```

---

# 🔄 End-to-End Data Flow

## 1. PDF Upload

The user uploads a company annual report through the Streamlit interface.

```text
annual_report.pdf
        ↓
Streamlit uploader
```

---

## 2. PDF Text Extraction

**PyMuPDF** extracts text from each page.

The system preserves the original page number so retrieved information can later be associated with its source.

```text
PDF Page 25
     ↓
Extracted text
     ↓
Page metadata = 25
```

---

## 3. Text Chunking

Large blocks of text are divided into smaller chunks using LangChain's `RecursiveCharacterTextSplitter`.

Current configuration:

```text
Chunk size: 1000 characters
Chunk overlap: 150 characters
```

The overlap helps preserve context between neighboring chunks.

---

## 4. Embedding Generation

Each text chunk is converted into a numerical vector using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Conceptually:

```text
"Revenue increased by 18%..."
              ↓
        Embedding Model
              ↓
      [0.12, -0.08, 0.44, ...]
```

These vectors allow the system to perform semantic similarity search.

---

# 🗄️ Vector Database

The project uses **ChromaDB** to store:

- Text chunks
- Embeddings
- PDF page numbers
- Chunk metadata

Example:

```text
Chunk
 ├── Text
 ├── Embedding
 ├── Page number
 └── Chunk index
```

When a user asks a question, the question is converted into an embedding and compared against the stored document embeddings.

The system retrieves the **Top 5 most relevant chunks**.

---

# 🔎 Semantic Retrieval

Suppose the user asks:

```text
How did the company's revenue change?
```

The system does not rely only on exact keyword matching.

Instead:

```text
Question
   ↓
Question Embedding
   ↓
Similarity Search
   ↓
Top 5 Relevant Chunks
```

This allows semantically related content to be retrieved even when the wording of the question differs from the wording in the report.

---

# 🤖 LLM Generation

The retrieved chunks are passed to **Google Gemini**.

The model is instructed to:

- Use only the supplied annual-report excerpts.
- Avoid inventing financial figures.
- Preserve currencies.
- Preserve financial years.
- Distinguish reported values from calculations.
- State when information is unavailable.
- Mention relevant PDF pages.
- Avoid personalized investment advice.

This creates a more controlled generation process than simply asking an LLM a financial question without document context.

---

# 📚 Source Grounding

One of the important features of the application is source visibility.

The application displays:

```text
Answer
   ↓
Retrieved Sources
   ↓
PDF Page Numbers
   ↓
Original Retrieved Text
```

This allows users to verify the generated answer against the original annual report.

For financial analysis, this is particularly important because a small numerical error can completely change the interpretation of a financial metric.

---

# 🧩 Technology Stack

| Component              | Technology                |
| ---------------------- | ------------------------- |
| Frontend               | Streamlit                 |
| Programming Language   | Python                    |
| PDF Processing         | PyMuPDF                   |
| Text Chunking          | LangChain Text Splitters  |
| Embeddings             | Sentence Transformers     |
| Embedding Model        | `all-MiniLM-L6-v2`        |
| Vector Database        | ChromaDB                  |
| LLM                    | Google Gemini API         |
| Environment Management | python-dotenv             |
| Containerization       | Docker                    |
| Version Control        | Git / GitHub              |
| Deployment             | Streamlit Community Cloud |

---

# 📁 Project Structure

```text
financial-statement-rag/
│
├── app.py
│
├── rag_engine.py
│
├── requirements.txt
│
├── Dockerfile
│
├── .gitignore
│
├── README.md
│
└── .streamlit/
    └── config.toml
```

### `app.py`

Responsible for the Streamlit user interface.

Handles:

- PDF upload
- PDF processing
- User questions
- Retrieval
- Answer generation
- Source display
- Error handling

---

### `rag_engine.py`

Contains the core RAG pipeline.

Handles:

- PDF extraction
- Text chunking
- Embedding generation
- ChromaDB storage
- Semantic retrieval
- Gemini API integration
- Prompt construction
- Model fallback handling

---

### `requirements.txt`

Contains the Python dependencies required to run the application.

---

### `Dockerfile`

Defines the containerized environment for running the application.

The project uses Python 3.12 inside Docker.

---

### `.gitignore`

Prevents sensitive and generated files from being committed.

Important ignored files include:

```text
.env
.venv/
vectorstore/
__pycache__/
```

---

# 🐳 Docker Architecture

The application can also be packaged as a Docker container.

```text
Dockerfile
     ↓
Python 3.12 Image
     ↓
Install Dependencies
     ↓
Copy Application
     ↓
Run Streamlit
```

The container exposes the Streamlit application through port `7860`.

Example Docker workflow:

```bash
docker build -t financial-statement-rag .
```

Run:

```bash
docker run -p 7860:7860 financial-statement-rag
```

The application can then be accessed locally through:

```text
http://localhost:7860
```

---

# ☁️ Deployment Architecture

The production deployment uses:

```text
                  GitHub
                     │
                     │ Source Code
                     ▼
          Streamlit Community Cloud
                     │
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
       Streamlit App      Secrets
             │          GEMINI_API_KEY
             │
             ▼
          Gemini API
```

### Deployment components

**GitHub**

Stores the source code and project history.

**Streamlit Community Cloud**

Hosts the Streamlit application.

**Streamlit Secrets**

Stores the Gemini API key securely.

**Google Gemini API**

Provides the language model used for answer generation.

---

# 🔐 API Key Security

The Gemini API key is never committed to the repository.

For local development:

```env
GEMINI_API_KEY=your_api_key
```

The `.env` file is excluded through `.gitignore`.

For Streamlit Cloud, the API key is stored using Streamlit's Secrets management.

Example:

```toml
GEMINI_API_KEY = "your_api_key"
```

Never expose API keys in:

- GitHub repositories
- Source code
- Screenshots
- README files
- Docker images
- Public logs

---

# ⚙️ Local Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-statement-rag.git
```

Move into the project:

```bash
cd financial-statement-rag
```

---

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Gemini

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 💻 Example Usage

### Step 1

Upload:

```text
Company_Annual_Report_2025.pdf
```

### Step 2

Click:

```text
Process & Index PDF
```

### Step 3

Ask:

```text
What was the company's net profit in FY2025?
```

### Step 4

The RAG system:

```text
Question
   ↓
Embedding
   ↓
ChromaDB Search
   ↓
Top 5 Relevant Chunks
   ↓
Gemini
   ↓
Answer
```

### Step 5

The application displays:

```text
📈 Answer

...

📚 Retrieved Sources

Source 1 • PDF Page 87
Source 2 • PDF Page 91
...
```

---

# 📊 Example Questions

The application can be used for questions such as:

### Revenue

```text
What was the company's revenue in FY2025?
```

### Profitability

```text
What was the net profit for FY2025?
```

### Year-over-year comparison

```text
How did revenue change between FY2024 and FY2025?
```

### Balance sheet

```text
What were the company's total assets?
```

### Liabilities

```text
What were the major liabilities reported?
```

### Cash flow

```text
What was the company's operating cash flow?
```

### Financial analysis

```text
What factors contributed to the change in revenue?
```

---

# 🛡️ Reliability and Guardrails

Because financial information requires accuracy, the system includes several prompt-level controls.

The LLM is instructed to:

```text
✓ Use only retrieved report information
✓ Avoid fabricated figures
✓ Preserve financial years
✓ Preserve currencies
✓ Show calculations when applicable
✓ Identify missing information
✓ Provide source page references
✓ Avoid personalized investment advice
```

The application also exposes the retrieved text so users can independently verify the generated response.

---

# ⚠️ Current Limitations

This is a portfolio and research project rather than a production-grade financial analysis platform.

### 1. PDF quality

Scanned PDFs or documents containing complex images and tables may not extract perfectly.

### 2. Tables

Financial reports frequently contain complex tables. Text extraction can sometimes disrupt their original structure.

### 3. Local vector storage

The current ChromaDB implementation uses local persistent storage.

For large-scale production systems, a managed or remote vector database would be more appropriate.

### 4. Retrieval quality

The quality of the final answer depends heavily on whether the correct document chunks are retrieved.

### 5. LLM limitations

Even with grounding, generated answers should be verified against the original report.

### 6. No investment recommendations

The application is designed for document analysis and research, not personalized investment decisions.

---

# 🔮 Future Improvements

Potential improvements include:

- [ ] Multi-document analysis
- [ ] Compare annual reports across multiple companies
- [ ] Automatic financial ratio calculation
- [ ] Revenue and profit trend visualization
- [ ] Financial statement table extraction
- [ ] Better handling of scanned PDFs using OCR
- [ ] Hybrid keyword + vector retrieval
- [ ] Reranking retrieved documents
- [ ] Metadata-aware retrieval
- [ ] Remote vector database
- [ ] Authentication and user accounts
- [ ] Conversation history
- [ ] Streaming LLM responses
- [ ] Automated evaluation of RAG retrieval quality
- [ ] RAG evaluation metrics
- [ ] Observability and monitoring
- [ ] Production MLOps pipeline

---

# 📈 Future Architecture

A more advanced version could evolve into:

```text
                     ┌───────────────────┐
                     │  Financial PDFs   │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ PDF + OCR Parser  │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ Document Chunking │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ Embedding Model   │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ Vector Database   │
                     └─────────┬─────────┘
                               │
                    Hybrid Retrieval
                               │
                               ▼
                     ┌───────────────────┐
                     │     Reranker      │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │      Gemini       │
                     └─────────┬─────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ Financial Answer  │
                     │ + Sources         │
                     └───────────────────┘
```

---

# 🎓 What This Project Demonstrates

This project demonstrates practical experience with:

### AI / Machine Learning

- Retrieval-Augmented Generation
- Text embeddings
- Semantic search
- Vector databases
- LLM integration
- Prompt engineering
- Document question answering

### Financial Technology

- Annual-report analysis
- Financial statement information retrieval
- Financial document processing
- Financial-year comparison
- Source-grounded financial analysis

### Software Engineering

- Python application development
- Modular RAG architecture
- API integration
- Error handling
- Environment variable management
- Git version control
- Docker containerization
- Cloud deployment

### Cloud / Deployment

- GitHub-based deployment
- Streamlit Community Cloud
- Secure API secret management
- Containerized application architecture

---

# 💼 Resume-Relevant Project Summary

### Financial Statement RAG Analyst

**Technologies:** Python, Streamlit, ChromaDB, Sentence Transformers, Gemini API, PyMuPDF, Docker

Built an end-to-end Retrieval-Augmented Generation application for analyzing company annual reports. Implemented PDF text extraction, semantic chunking, embedding generation with Sentence Transformers, vector search using ChromaDB, and grounded financial question answering with Google Gemini. Added source-page retrieval and prompt guardrails to reduce unsupported financial claims, and containerized and deployed the application using Docker and Streamlit Community Cloud.

---

# 📌 Resume Bullet Points

These are the strongest points to use on your resume:

- **Built an end-to-end RAG application for financial annual-report analysis using Python, Streamlit, ChromaDB, Sentence Transformers, and Google Gemini API.**

- **Implemented PDF extraction, recursive text chunking, semantic embeddings, vector similarity retrieval, and source-aware LLM generation for document-grounded financial question answering.**

- **Designed prompt guardrails to reduce hallucinated financial figures, preserve reporting periods and currencies, and expose relevant source PDF pages for answer verification.**

- **Containerized the application with Docker and deployed the Streamlit application using GitHub and Streamlit Community Cloud with secure Gemini API secret management.**

---

# 🏷️ Project Tags

```text
RAG
Retrieval-Augmented Generation
Generative AI
LLM
Artificial Intelligence
Machine Learning
FinTech
Financial AI
Financial Analysis
NLP
Semantic Search
Vector Database
ChromaDB
Sentence Transformers
Gemini
Python
Streamlit
Docker
GitHub
```

---

# 📜 Disclaimer

This project is intended for educational and research purposes.

The generated responses may contain errors. Financial figures and interpretations should always be verified against the original company annual report.

This application does not provide personalized financial or investment advice.

---

# 👨‍💻 Author

**Vishal Singoju**

B.Tech Graduate | AI/ML Enthusiast | FinTech & AI

GitHub: `https://github.com/VishalSingoju`

---

## ⭐ If you find this project useful

Consider starring the repository and exploring the implementation.

Built to explore the intersection of **Generative AI, Retrieval-Augmented Generation, and Financial Technology**.
