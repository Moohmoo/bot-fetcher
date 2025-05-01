"""Chunker module for splitting documents into smaller pieces."""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
import hashlib
import logging
from logging_configuration import setup_logging

# Configuration for logging
setup_logging()
logger = logging.getLogger(__name__)


def chunk_document(documents: list[Document]) -> list[Document]:
    """
    Chunk documents into smaller pieces using RecursiveCharacterTextSplitter.

    Parameters:
    ----------
        - documents (list[Document]): List of Document objects to be chunked.

    Returns:
    -------
        - list[Document]: List of chunked Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    logger.info(f"Chunking {len(documents)} documents into smaller pieces.")
    return text_splitter.split_documents(documents)


def calculate_chunk_ids(chunks: list[Document]) -> list[Document]:
    """
    Calculate unique IDs for each chunk based on its content and metadata.

    Parameters:
    ----------
        - chunks (list[Document]): List of Document objects to calculate IDs
          for.

    Returns:
    -------
        - list[Document]: List of Document objects with updated metadata
          containing IDs.
    """
    for chunk in chunks:
        source_id = chunk.metadata.get('source_id', '')
        page_content = chunk.page_content.strip()
        base_str = f"{source_id}-{page_content}"
        chunk_id = hashlib.sha256(base_str.encode("utf-8")).hexdigest()
        chunk.metadata["id"] = chunk_id
    logging.info(f"Calculated IDs for {len(chunks)} chunks.")
    return chunks
