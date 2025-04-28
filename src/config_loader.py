"""Module for loading and accessing configuration settings."""

import configparser
import pathlib
import logging

# Configuration for logging
CONFIG_FILE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent 
    / "config" 
    / "config.cfg"
)
# Initialize the config parser
config = configparser.ConfigParser()
# Read the configuration file
if not CONFIG_FILE_PATH.exists():
    logging.critical(f"Configuration file not found at: {CONFIG_FILE_PATH}")
    raise FileNotFoundError(
        f"Configuration file not found at: {CONFIG_FILE_PATH}"
    )
else:
    try:
        config.read(CONFIG_FILE_PATH)
        logging.info(
            f"Configuration loaded successfully from: {CONFIG_FILE_PATH}"
        )
    except configparser.Error as e:
        logging.critical(
            f"Error reading configuration file {CONFIG_FILE_PATH}: {e}"
        )
        raise


def get_path(key: str) -> str:
    """Retrieve a path from the [Paths] section.

    Parameters:
    ----------
        - key (str): The key for the path to retrieve.

    Returns:
    -------
        - str: The path associated with the key.
    """
    return config.get('Paths', key)


def get_chromadb_config(key: str) -> str:
    """Retrieve a configuration value from the [ChromaDB] section.

    Parameters:
    ----------
        - key (str): The key for the configuration value to retrieve.

    Returns:
    -------
        - str: The configuration value associated with the key.
    """
    return config.get('ChromaDB', key)


def get_model_param(key: str, type_func=int):
    """Retrieve a model parameter from the [Models] section.

    Also handles type conversion.

    Parameters:
    ----------
        - key (str): The key for the model parameter to retrieve.
        - type_func (type): The type to convert the value to (default is int).

    Returns:
    -------
        - int/float/bool/str: The model parameter value associated with the
          key,converted to the specified type.
    """
    if type_func == int:
        return config.getint('Models', key)
    elif type_func == float:
        return config.getfloat('Models', key)
    elif type_func == bool:
        return config.getboolean('Models', key)
    else:
        return config.get('Models', key)


def get_rag_param(key: str, type_func=int):
    """Retrieve a RAG parameter from the [RAG] section.

    Also handles type conversion.

    Parameters:
    ----------
        - key (str): The key for the RAG parameter to retrieve.
        - type_func (type): The type to convert the value to (default is int).

    Returns:
    -------
        - int/float/bool/str: The RAG parameter value associated with the key,
          converted to the specified type.
    """
    if type_func == int:
        return config.getint('RAG', key)
    else:
        return config.get('RAG', key)


def get_logging_level() -> str:
    """Retrieve the logging level.

    Returns:
    -------
        - str: The logging level as a string (e.g., 'DEBUG', 'INFO',
          'WARNING', etc.).
    """
    return config.get('Logging', 'level', fallback='INFO').upper()


def get_scraping_param(key: str, type_func=int):
    """Retrieve a scraping parameter from the [Scraping] section.

    Also handles type conversion.

    Parameters:
    ----------
        - key (str): The key for the scraping parameter to retrieve.
        - type_func (type): The type to convert the value to (default is int).

    Returns:
    -------
        - int/float/bool/str: The scraping parameter value associated with the
          key, converted to the specified type.
    """
    if type_func == int:
        return config.getint('Scraping', key)
    else:
        return config.get('Scraping', key)


if __name__ == "__main__":
    # Example usage in this module (for testing)
    print(f"LLM Model Path: {get_path('llm_model')}")
    print(f"Chroma Collection: {get_chromadb_config('collection_name')}")
    print(f"LLM n_ctx: {get_model_param('n_ctx')}")
    print(f"RAG K: {get_rag_param('similarity_k')}")
    print(f"Logging Level: {get_logging_level()}")
