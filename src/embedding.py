"""Module to get the embedding function for the Ollama model."""

import logging
from logging_configuration import setup_logging
from langchain_community.embeddings import LlamaCppEmbeddings

# Configuration for logging
setup_logging()
logger = logging.getLogger(__name__)


def get_embedding_function(model_path: str) -> LlamaCppEmbeddings:
    """
    Get the LangChain embedding function wrapper for the Llama model.

    Args:
    ----
        - model_path (str): Path to the GGUF embedding model file.

    Returns:
    -------
        - LlamaCppEmbeddings: The LangChain embedding function wrapper.
    """
    try:
        embeddings = LlamaCppEmbeddings(
            model_path=model_path,
            verbose=False
        )
        logger.info("Embeddings function initialized successfully.")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize LlamaCppEmbeddings: {e}")
        raise
