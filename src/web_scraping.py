"""Web scraping module to extract text from various sources."""

import requests
from bs4 import BeautifulSoup
from newspaper import Article
import fitz  # PyMuPDF
from langchain.schema import Document
import hashlib
import logging
from logging_configuration import setup_logging

# ---------------------- Logging configuration ---------------------- #
setup_logging()
logger = logging.getLogger(__name__)

# ---------------------- Scrapers Functions ---------------------- #
def newspaper_scraper(url: str) -> str:
    """
    Use Newspaper3k to extract text from the article.
    
    Parameters:
    ----------
        - url (str): The URL of the article to scrape.
        
    Returns:
    -------
        - str: The extracted text from the article.
    """
    try:
        # Initialize the Article object
        article = Article(url)
        # Download and parse the article
        article.download()
        article.parse()
        if len(article.text) < 100:
            logger.warning(f"[Newspaper] Article too short: {url}")
            return "Error"
        return article.text.strip()
    except Exception as e:
        logger.warning(f"[Newspaper] Failed to fetch {url}: {e}")
        return "Error"

def beautifulsoup_scraper(html: str) -> str:
    """
    Use BeautifulSoup to extract text from HTML content.
    
    Parameters:
    ----------
        - html (str): The HTML content to parse.
        
    Returns:
    -------
        - str: The extracted text from the HTML content.
    """
    try:
        # Parse the HTML content
        soup = BeautifulSoup(html, "html.parser")
        content = soup.get_text(separator="\n", strip=True)
        if len(content) < 100:
            logger.warning(f"[BeautifulSoup] Content too short")
            return "Error"
        return content
    except Exception as e:
        logger.warning(f"[BeautifulSoup] Parsing error: {e}")
        return "Error"

def pdf_scraper(pdf_bytes: bytes, url: str) -> str:
    """
    Use PyMuPDF to extract text from PDF content.
    
    Parameters:
    ----------
        - pdf_bytes (bytes): The PDF content in bytes.
        - url (str): The URL of the PDF to scrape.
        
    Returns:
    -------
        - str: The extracted text from the PDF content.
    """
    try:
        # Open the PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        logger.warning(f"[PDF] Error extracting from {url}: {e}")
        return "Error"
    
def build_document(content: str, url: str, source_id: str, doc_type: str) -> Document:
    """Build a LangChain Document object from the content and metadata.
    
    Parameters:
    ----------
        - content (str): The extracted text content.
        - url (str): The URL of the source.
        - source_id (str): A unique identifier for the source.
        - doc_type (str): The type of document (e.g., "PDF", "Article", "HTML").
        
    Returns:
    -------
        - Document: A LangChain Document object containing the extracted text and metadata.
    """
    # Clean the text to ensure it's UTF-8 encoded
    clean_text = content.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    return Document(
        page_content=clean_text,
        metadata={
            "source": url,
            "source_id": source_id,
            "type": doc_type
        }
    )
    
def fetch_url(url: str) -> requests.Response:
    """Fetch the content from a URL.
    
    Parameters:
    ----------
        - url (str): The URL to fetch.
        
    Returns:
    -------
        - requests.Response: The HTTP response object.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        raise Exception(f"[SCRAPER] HTTP error for {url}: {e}")
    
def hash_url(url: str) -> str:
    """
    Hash the URL to create a unique source ID.
    
    Parameters:
    ----------
        - url (str): The URL to hash.
        
    Returns:
    -------
        - str: The hashed URL as a unique identifier.
    """
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def handle_pdf(response: requests.Response, url: str, source_id: str) -> Document:
    """
    Handle PDF content extraction.
    
    Parameters:
    ----------
        - response (requests.Response): The HTTP response object containing the PDF content.
        - url (str): The URL of the PDF.
        - source_id (str): A unique identifier for the source.
        
    Returns:
    -------
        - Document: A LangChain Document object containing the extracted text and metadata.
    """
    content = pdf_scraper(response.content, url)
    if content == "Error":
        raise Exception(f"[SCRAPER] Failed to extract PDF: {url}")

    logger.info(f"[SCRAPER] PDF extracted successfully: {url}")
    return build_document(content, url, source_id, "PDF")

def handle_html_or_article(response: requests.Response, url: str, source_id: str) -> Document:
    """
    Handle HTML or article content extraction.
    
    Parameters:
    ----------
        - response (requests.Response): The HTTP response object containing the HTML content.
        - url (str): The URL of the HTML or article.
        - source_id (str): A unique identifier for the source.
        
    Returns:
    -------
        - Document: A LangChain Document object containing the extracted text and metadata.
    """
    content = newspaper_scraper(url)
    if content != "Error":
        logger.info(f"[SCRAPER] Newspaper3k used for {url}")
        return build_document(content, url, source_id, "Article")

    content = beautifulsoup_scraper(response.text)
    if content != "Error":
        logger.info(f"[SCRAPER] BeautifulSoup used for {url}")
        return build_document(content, url, source_id, "HTML")

    raise Exception(f"[SCRAPER] Complete failure for {url}")

    
def fetch_content(url: str) -> Document:
    response = fetch_url(url)
    content_type = response.headers.get("Content-Type", "")
    source_id = hash_url(url)

    if "application/pdf" in content_type:
        return handle_pdf(response, url, source_id)
    
    return handle_html_or_article(response, url, source_id)

# ---------------------- Test ---------------------- #
if __name__ == "__main__":
    url = "https://storage.googleapis.com/deepmind-media/Era-of-Experience%20/The%20Era%20of%20Experience%20Paper.pdf"
    url = "https://arxiv.org/abs/2504.16115"
    print(fetch_content(url))
