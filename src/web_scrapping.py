""" Web scraping module to extract text from various sources."""

import requests
import logging
from bs4 import BeautifulSoup
from newspaper import Article
import fitz  # PyMuPDF

# ---------------------- Logging ---------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Scrapers ---------------------- #
def newspaper_scrapper(url: str) -> str:
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
        return article.text.strip()
    except Exception as e:
        logger.warning(f"[Newspaper] Failed to fetch {url}: {e}")
        return "Error"

def beautifulsoup_scrapper(html: str) -> str:
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
        return content
    except Exception as e:
        logger.warning(f"[BeautifulSoup] Parsing error: {e}")
        return "Error"

def pdf_scrapper(pdf_bytes: bytes, url: str) -> str:
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

def fetch_content(url: str) -> str:
    """
    Try Newspaper3k first, fallback to BeautifulSoup, detect and parse PDF if needed.
    
    Parameters:
    ----------
        - url (str): The URL to scrape.
        
    Returns:
    -------
        - str: The extracted text from the URL.
    """
    # URL validation
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"[SCRAPER] 🚫 Erreur HTTP pour {url}: {e}")

    # Check if the content is a PDF
    content_type = response.headers.get("Content-Type", "")
    if "application/pdf" in content_type:
        content = pdf_scrapper(response.content, url)
        if content != "Error":
            logger.info(f"[SCRAPER] ✅ PDF extrait : {url}")
            return content
        raise Exception(f"[SCRAPER] ❌ Échec extraction PDF : {url}")

    # Check if is article
    content = newspaper_scrapper(url)
    if content != "Error":
        logger.info(f"[SCRAPER] ✅ Newspaper3k utilisé pour {url}")
        return content

    # Fallback to BeautifulSoup
    content = beautifulsoup_scrapper(response.text)
    if content != "Error":
        logger.info(f"[SCRAPER] ✅ BeautifulSoup utilisé pour {url}")
        return content

    raise Exception(f"[SCRAPER] ❌ Échec complet pour {url}")


# ---------------------- Test ---------------------- #
if __name__ == "__main__":
    url = "https://storage.googleapis.com/deepmind-media/Era-of-Experience%20/The%20Era%20of%20Experience%20Paper.pdf"
    print(fetch_content(url))
