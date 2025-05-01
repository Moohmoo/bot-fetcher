"""Ingest URLs and update the Chroma database with new chunks."""

from pathlib import Path
from langchain.schema import Document
from langchain_chroma import Chroma
from embedding import get_embedding_function
from chunker import calculate_chunk_ids, chunk_document
import sqlite3
from web_scraping import fetch_content
import logging
from logging_configuration import setup_logging
import pathlib
from config_loader import get_path, get_chromadb_config

# Configuration for logging
setup_logging()
logger = logging.getLogger(__name__)

# Project root directory
project_root = pathlib.Path(__file__).resolve().parent.parent.parent
# Get the database filename and Chroma DB directory name from config
db_filename = get_path("sqlite_db")
chroma_db_dirname = get_path("chroma_db")
EMBED_MODEL = get_path("embedding_model")
COLLECTION_NAME = get_chromadb_config("collection_name")
# Paths to the SQLite database and Chroma DB
DB_PATH = project_root / db_filename
CHROMA_DB_PATH = project_root / chroma_db_dirname
EMBEDDING_MODEL_PATH = project_root / EMBED_MODEL
logger.info(f"SQLite DB path set to: {DB_PATH}")
logger.info(f"Chroma DB path set to: {CHROMA_DB_PATH}")
logger.info(f"Embedding model path set to: {EMBEDDING_MODEL_PATH}")
logger.info(f"Chroma collection name: {COLLECTION_NAME}")


def db_exists() -> bool:
    """Check if the database file exists.

    Returns:
    -------
        - bool: True if the database file exists, False otherwise.
    """
    return DB_PATH.exists()


def get_pending_urls(con: sqlite3.Connection) -> list[tuple[str, str]]:
    """Fetch URLs that have not been ingested yet.

    Parameters:
    ----------
        - con (sqlite3.Connection): SQLite connection object.

    Returns:
    -------
        - list[tuple[str, str]]: List of tuples containing URLs not yet
          ingested.
    """
    cur = con.cursor()
    cur.execute("SELECT url, published FROM urls WHERE ingested = 0")
    logger.info(f"Fetching pending URLs from the database.")
    return cur.fetchall()


def mark_urls_as_ingested(con: sqlite3.Connection, urls: list[str]):
    """Mark the given URLs as ingested in the database.

    Parameters:
    ----------
        - con (sqlite3.Connection): SQLite connection object.
        - urls (list[str]): List of URLs to mark as ingested.
    """
    cur = con.cursor()
    cur.executemany(
        "UPDATE urls SET ingested = 1 WHERE url = ?", [(url,) for url in urls]
    )
    con.commit()


def initialize_chroma_db() -> Chroma:
    """Initialize the Chroma database.

    Returns:
    -------
        - Chroma: The initialized Chroma database object.
    """
    embedding_func = get_embedding_function(str(EMBEDDING_MODEL_PATH))
    chroma = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embedding_func,
        collection_name=COLLECTION_NAME,
    )
    logger.info(f"Chroma DB initialized at `{CHROMA_DB_PATH}`")
    return chroma


def filter_new_chunks(db: Chroma, chunks: list[Document]) -> list[Document]:
    """Filter out chunks that already exist in the Chroma database.

    Parameters:
    ----------
        - db (Chroma): The Chroma database object.
        - chunks (list[Document]): List of Document objects to filter.

    Returns:
    -------
        - list[Document]: List of Document objects that are new and not in
          the database.
    """
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_chunks = db.get(include=[])
    existing_ids = set(existing_chunks["ids"])
    logger.info(f"Existing chunk IDs: {len(existing_ids)}")
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
    return new_chunks


def add_chunks_to_chroma(db: Chroma, chunks: list[Document]):
    """Add new chunks to the Chroma database.

    Parameters:
    ----------
        - db (Chroma): The Chroma database object.
        - chunks (list[Document]): List of Document objects to add to the
          database.
    """
    if chunks:
        logger.info(f"Adding {len(chunks)} new chunks to Chroma DB.")
        new_chunk_ids = [chunk.metadata["id"] for chunk in chunks]
        db.add_documents(chunks, ids=new_chunk_ids)
    else:
        logger.info("No new chunks to add to Chroma DB.")


def process_urls(
    urls: list[tuple[str, str]]
) -> tuple[list[Document], list[str]]:
    """Fetch content for URLs and return documents and successfully ingested.

    Parameters:
    ----------
        - urls (list[tuple[str, str]]): List of tuples containing URLs
          to fetch.

    Returns:
    -------
        - tuple[list[Document], list[str]]: Tuple containing a list of Document
          objects and a list of successfully ingested URLs.
    """
    docs, ingested_urls = [], []
    for url, _ in urls:
        try:
            docs.append(fetch_content(url))
            ingested_urls.append(url)
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
    return docs, ingested_urls


def run_pipeline():
    """Pipeline to process URLs and update the Chroma database."""
    if not db_exists():
        logger.error(f"DB file not found: {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as con:
        urls = get_pending_urls(con)
        if not urls:
            logger.info("No URLs to process.")
            return

        docs, ingested_urls = process_urls(urls)
        if not docs:
            logger.info("No documents fetched.")
            return

        db = initialize_chroma_db()
        new_chunks = filter_new_chunks(db, chunk_document(docs))
        add_chunks_to_chroma(db, new_chunks)
        mark_urls_as_ingested(con, ingested_urls)
        logger.info(
            f"Pipeline completed. Chroma DB saved at `{CHROMA_DB_PATH}`"
        )


if __name__ == "__main__":
    run_pipeline()
