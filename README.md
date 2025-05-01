<div align="center">

# Bot-Fetcher: Local RAG Q&A System

*Your personal assistant for exploring and querying your information streams.*

<p>
    <a href="https://github.com/Moohmoo/bot-fetcher/commits/main">
        <img src="https://img.shields.io/github/last-commit/Moohmoo/bot-fetcher" alt="GitHub last commit"/>
    </a>
    <img src="https://img.shields.io/badge/Python-3.13-blue" alt="Python Version"/>
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"/>
</p>

</div>

## Description 
Bot-Fetcher is a Python-based system designed to answer questions based on content fetched from various web sources (RSS feeds, web pages, PDFs). It utilizes a Retrieval-Augmented Generation (RAG) pipeline powered by local Large Language Models (LLMs) and vector embeddings, offline capability.

## Features

*   **RSS Feed Aggregation:** Fetches articles from multiple RSS feeds using `feedparser`.
*   **Web Content Scraping:** Extracts text content from:
    *   Web articles (`newspaper3k`)
    *   General HTML pages (`BeautifulSoup4`)
    *   PDF documents (`PyMuPDF/fitz`)
*   **Data Management:** Uses SQLite to track URLs to be processed.
*   **Content Chunking:** Splits large documents into smaller, manageable chunks (`langchain_text_splitters`).
*   **Local Embeddings:** Generates text embeddings locally using `LlamaCppEmbeddings`.
*   **Vector Storage:** Stores document chunks and their embeddings in a persistent ChromaDB database.
*   **Local RAG Pipeline:**
    *   Retrieves relevant document chunks based on user query similarity.
    *   Uses a local LLM (via `llama-cpp-python`) to generate answers based on the retrieved context.
*   **Configurable:** Easily configure paths, model parameters, and scraping settings via `config/config.cfg`.

## Tech Stack

*   **Programming Language:** Python 3.13
*   **Core Libraries:**
    *   LangChain: Framework for building LLM applications (Core, Community, Text Splitters, Chroma).
    *   `llama-cpp-python`: Python bindings for llama.cpp to run LLMs locally.
    *   ChromaDB: Vector database for storing and retrieving embeddings.
    *   SQLite: For managing URLs and feed sources.
*   **Web Scraping:** `requests`, `BeautifulSoup4`, `newspaper3k`, `PyMuPDF`
*   **RSS Parsing:** `feedparser`
*   **Environment Management:** Conda

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Moohmoo/bot-fetcher
    cd bot-fetcher
    ```

2.  **Create Conda Environment:**
    ```bash
    conda env create -f environment.yml
    conda activate bot-fetcher-env
    ```
    *Note: `llama-cpp-python` installation might require specific build tools depending on your OS and whether you want GPU acceleration. Refer to the official `llama-cpp-python` documentation if you encounter issues.*

3.  **Download Models:**
    *   Download the GGUF format LLM and Embedding models you intend to use.
    *   Place them inside the `models/` directory.
    *   Example models used in `config.cfg`:
        *   LLM: `Phi-3-mini-4k-instruct-q4.gguf`
        *   Embedding: `mxbai-embed-large-v1-f16.gguf`

4.  **Configure:**
    *   Review and update `config/config.cfg` to match the paths to your downloaded models (`llm_model`, `embedding_model`) and adjust other parameters (e.g., `n_ctx`, `similarity_k`) as needed.
    *   The `data/` directory and the SQLite database (`urls_to_ingest.db`) will be created automatically when `fetch_rss.py` or `ingest.py` is run for the first time.

## Configuration (`config/config.cfg`)

*   **[Paths]:** Defines paths for ChromaDB, SQLite DB, and model files.
*   **[ChromaDB]:** Specifies the collection name within ChromaDB.
*   **[Models]:** Parameters for the LLM (e.g., context size `n_ctx`, `n_threads`).
*   **[RAG]:** Parameters for the RAG process (e.g., number of chunks to retrieve `similarity_k`).
*   **[Logging]:** Sets the logging level (e.g., `INFO`, `DEBUG`).
*   **[Scraping]:** Parameters for web scraping (e.g., `timeout`, `min_content_length`).

## Usage

The workflow generally involves adding RSS feeds, fetching items from them (which populates the URL database), ingesting the content (scraping, chunking, embedding, storing), and finally querying.

1.  **Manage RSS Feeds:**
    *   **Add a feed:**
        ```bash
        python src/fetch_rss.py --add "Example Blog" "https://example.com/rss"
        ```
    *   **List feeds:**
        ```bash
        python src/fetch_rss.py --list
        ```
    *   **Delete a feed:**
        ```bash
        python src/fetch_rss.py --delete "Example Blog"
        ```

2.  **Fetch RSS Feed Items:**
    *   This command fetches items from all registered feeds and adds their URLs to the `urls_to_ingest.db` database, marked as `ingested = 0`.
        ```bash
        python src/fetch_rss.py --fetch
        ```

3.  **Ingest Content:**
    *   This script processes URLs marked with `ingested = 0` in the database. It fetches the content, chunks it, generates embeddings, and stores the chunks in ChromaDB. Processed URLs are marked as `ingested = 1`.
        ```bash
        python src/ingest.py
        ```

4.  **Query the System:**
    *   Ask questions based on the ingested content. The script performs a similarity search in ChromaDB, retrieves relevant chunks, and feeds them along with your question to the local LLM.
        ```bash
        python src/rag_query.py "What is the main topic discussed about OpenAI?"
        ```

## TODO / Améliorations Possibles

* Add unit and integration tests.
* Improve error handling (scraping, LLM).
* Develop a user interface (Streamlit, Gradio, Flask, etc.).
* Optimize performance (GPU offloading, faster models).

