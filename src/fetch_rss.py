"""Module to fetch RSS feeds and save them to a SQLite database."""

import feedparser
import sqlite3
import datetime
import argparse
from config_loader import get_path
import logging
from logging_configuration import setup_logging
import pathlib

# Configuration for logging
setup_logging()
logger = logging.getLogger(__name__)

# Constants for database
db_filename = get_path("sqlite_db")
project_root = pathlib.Path(__file__).resolve().parent.parent.parent
DB_PATH = project_root / db_filename
logger.info(f"SQLite DB path set to: {DB_PATH}")


def init_db():
    """Initialize the SQLite database and create tables if not exist."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            url       TEXT PRIMARY KEY,
            title     TEXT,
            published TEXT,
            source    TEXT,
            ingested  INTEGER DEFAULT 0
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feeds (
            name TEXT PRIMARY KEY,
            url  TEXT NOT NULL
        );
    """)
    con.commit()
    logger.info("Database initialized and tables created.")
    con.close()


def db_exists() -> bool:
    """Check if the database file exists.

    Returns:
    -------
        bool: True if the database file exists, False otherwise.
    """
    return DB_PATH.exists()


def save_item(url: str, title: str, date: str, source: str):
    """Save a new item to the database, ignoring duplicates.

    Parameters:
    ----------
        url : str
            The URL of the item.
        title : str
            The title of the item.
        date : str
            The publication date of the item.
        source : str
            The source of the item.
    """
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute(
            "INSERT INTO urls(url, title, published, source) VALUES(?,?,?,?)",
            (url, title, date, source)
        )
        con.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        con.close()


def fetch_all():
    """Fetch all RSS feeds and save new items to the database."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name, url FROM feeds")
    feeds = cur.fetchall()
    con.close()

    total_items = 0
    for src, feed_url in feeds:
        d = feedparser.parse(feed_url)
        for entry in d.entries:
            url = entry.link
            title = entry.title
            date = entry.get(
                "published",
                datetime.datetime.now(datetime.timezone.utc).isoformat()
            )
            logger.info(f"Fetched item: {title} from {src}")
            save_item(url, title, date, src)
        total_items += len(d.entries)
    logger.info(
        "All feeds fetched and saved to the database. Total items: %d",
        total_items
    )


def add_feed(name: str, url: str):
    """Add a new RSS feed to the database.

    Parameters:
    ----------
        name : str
            The name of the feed.
        url : str
            The URL of the feed.
    """
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT OR REPLACE INTO feeds(name, url) VALUES(?, ?)",
        (name, url)
    )
    con.commit()
    con.close()


def delete_feed(name: str):
    """Delete a feed from the database.

    Parameters:
    ----------
        name : str
            The name of the feed to delete.
    """
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM feeds WHERE name = ?", (name,))
    con.commit()
    con.close()


def list_feeds() -> list[tuple[str, str]]:
    """List all RSS feeds in the database.

    Returns:
    -------
        list[tuple[str, str]]: A list of tuples containing feed names and URLs.
    """
    con = sqlite3.connect(DB_PATH)
    feeds = con.execute("SELECT name, url FROM feeds").fetchall()
    con.close()
    return feeds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bot Fetcher - RSS Feed & Scraper CLI"
    )

    parser.add_argument(
        "--fetch", action="store_true",
        help="Fetch all RSS feeds and update DB"
    )
    parser.add_argument(
        "--add", nargs=2, metavar=("NAME", "URL"), help="Add a new feed"
    )
    parser.add_argument(
        "--delete", metavar="NAME", help="Delete a feed by name"
    )
    parser.add_argument("--list", action="store_true", help="List all feeds")

    args = parser.parse_args()

    if not db_exists():
        init_db()

    if args.fetch:
        fetch_all()

    if args.add:
        name, url = args.add
        add_feed(name, url)
        logger.info(f"Feed added: {name} - {url}")

    if args.delete:
        delete_feed(args.delete)
        logger.info(f"Feed deleted: {args.delete}")

    if args.list:
        feeds = list_feeds()
        logger.info("Listing all feeds:")
        for name, url in feeds:
            logger.info(f"{name}: {url}")
