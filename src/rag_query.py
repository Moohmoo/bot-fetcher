"""This script implements a local RAG pipeline using Llama and Chroma."""

import argparse
from embedding import get_embedding_function
from langchain_chroma import Chroma
import llama_cpp
import logging
from logging_configuration import setup_logging
from config_loader import get_chromadb_config
from config_loader import get_model_param
import pathlib
from config_loader import get_rag_param
from config_loader import get_path

# Configuration for logging
setup_logging()
logger = logging.getLogger(__name__)

# Project root directory
project_root = pathlib.Path(__file__).resolve().parent.parent.parent
# Get the database filename, Chroma DB directory name from config and others
chroma_db_dirname = get_path("chroma_db")
llm_model_rel_path = get_path("llm_model")
embedding_model_rel_path = get_path("embedding_model")
COLLECTION_NAME = get_chromadb_config("collection_name")
n_ctx = get_model_param("n_ctx")  # Parameter LLM
n_threads = get_model_param("n_threads")
similarity_k = get_rag_param("similarity_k")  # Parameter RAG
# Build the paths to the SQLite database and Chroma DB
CHROMA_DB_PATH = project_root / chroma_db_dirname
MODEL_PATH = project_root / llm_model_rel_path
EMBED_PATH = project_root / embedding_model_rel_path
logger.info(f"Chroma DB path set to: {CHROMA_DB_PATH}")
logger.info(f"LLM model path set to: {MODEL_PATH}")
logger.info(f"Embedding model path set to: {EMBED_PATH}")
logger.info(f"Chroma collection name: {COLLECTION_NAME}")
logger.info(f"LLM n_ctx: {n_ctx}, n_threads: {n_threads}")
logger.info(f"RAG similarity k: {similarity_k}")

# Prompt template for the Llama model
PROMPT_TEMPLATE = (
    "Answer the following question: {question} based only on the following"
    "context:\n{context}\n\n"
    "---\n"
    "Give me only the answer, do not add any other information.\n"
    "If the question is not in the context, say 'Your question is out of"
    "context from the documents I have'.\n"
)


def initialize_llama(
    model_path: str,
    n_ctx: int = 4096,
    n_threads: int = 8
) -> llama_cpp.Llama:
    """Initialize the Llama model.

    Parameters:
    ----------
        - model_path (str): Path to the Llama model.
        - n_ctx (int): Context size for the model.
        - n_threads (int): Number of threads to use for inference.

    Returns:
        - llama_cpp.Llama: Initialized Llama model.
    """
    return llama_cpp.Llama(
        model_path=str(model_path),
        n_ctx=n_ctx,
        verbose=False,
        n_threads=n_threads
    )


def format_prompt(context: str, question: str) -> str:
    """Format the prompt using the template.

    Parameters:
    ----------
        - context (str): Context to include in the prompt.
        - question (str): Question to include in the prompt.

    Returns:
    -------
        - str: Formatted prompt string.
    """
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_response(llama_model, query: str, prompt_text: str):
    """Generate a response using the Llama model.

    Parameters:
    ----------
        - llama_model (llama_cpp.Llama): Initialized Llama model.
        - query (str): Question to ask the model.
        - prompt_text (str): Context to include in the prompt.
    """
    logger.info("Generating response from the LLM ...")
    template = format_prompt(prompt_text, query)
    stream = llama_model.create_chat_completion(
        messages=[{"role": "user", "content": template}],
        stream=True,
    )
    for chunk in stream:
        print(chunk["choices"][0]["delta"].get("content", ""), end="")
    print("\n")


def search_relevant_chunks(query_text: str) -> str:
    """Search for relevant chunks in the Chroma database.

    Parameters:
    ----------
        - query_text (str): Query text to search for.

    Returns:
    -------
        - str: Concatenated text of the relevant chunks.
    """
    embedding_function = get_embedding_function(str(EMBED_PATH))
    db = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME,
    )
    logger.info("Searching for relevant chunks for the query ...")
    results = db.similarity_search_with_score(query_text, k=3)
    logger.info(f"Found {len(results)} relevant chunks.")
    return "\n\n---\n\n".join([doc.page_content for doc, _ in results])


def query_rag(query_text: str):
    """Query the RAG pipeline.

    Parameters:
    ----------
        - query_text (str): Query text to search for.
    """
    logger.info(f"Querying RAG with the question: {query_text}")
    context_text = search_relevant_chunks(query_text)
    llama_model = initialize_llama(MODEL_PATH)
    generate_response(llama_model, query_text, context_text)


def command_line_interface():
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Ask a question using local RAG pipeline."
    )
    parser.add_argument(
        "question",
        type=str,
        help="Your question to the RAG engine."
    )
    args = parser.parse_args()
    query_rag(args.question)


if __name__ == "__main__":
    command_line_interface()
