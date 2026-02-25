"""Placeholder script for scraping ANSYS documentation.

Data sources to target:
- ANSYS APDL Command Reference (https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/corp/v232/en/ans_cmd/Hlp_C_CmdTOC.html)
- PyANSYS / PyMAPDL documentation (https://mapdl.docs.pyansys.com/)
- ANSYS Element Reference
- ANSYS Verification Manual examples
- ANSYS Meshing User Guide

Note: Always respect robots.txt and terms of service when scraping.
      Consider using the official ANSYS developer portal or downloading
      documentation PDFs directly where permitted.
"""

import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Output directory for raw scraped content
OUTPUT_DIR = Path("backend/knowledge_base/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Example publicly accessible PyANSYS docs pages
PYMAPDL_DOCS_URLS: list[str] = [
    "https://mapdl.docs.pyansys.com/version/stable/getting_started/index.html",
    # Add more URLs as needed
]


def scrape_page(url: str, delay: float = 1.0) -> str:
    """Fetch a single web page and extract its main text content.

    Args:
        url: The URL to scrape.
        delay: Seconds to wait after the request (rate limiting).

    Returns:
        Extracted plain text from the page, or empty string on failure.
    """
    headers = {"User-Agent": "ansys-copilot-scraper/0.1 (educational project)"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove navigation, footer, and script elements
        for tag in soup(["nav", "footer", "script", "style", "header"]):
            tag.decompose()

        # Extract main content
        main = soup.find("main") or soup.find("article") or soup.find("body")
        text = main.get_text(separator="\n", strip=True) if main else ""
        time.sleep(delay)
        return text
    except Exception as exc:
        print(f"Failed to scrape {url}: {exc}")
        return ""


def save_document(content: str, filename: str) -> None:
    """Save scraped content to a text file.

    Args:
        content: Text content to save.
        filename: Output filename (without directory prefix).
    """
    output_path = OUTPUT_DIR / filename
    output_path.write_text(content, encoding="utf-8")
    print(f"Saved: {output_path}")


def main() -> None:
    """Scrape configured documentation sources."""
    print(f"Scraping {len(PYMAPDL_DOCS_URLS)} pages…")
    for i, url in enumerate(PYMAPDL_DOCS_URLS, start=1):
        print(f"[{i}/{len(PYMAPDL_DOCS_URLS)}] {url}")
        text = scrape_page(url)
        if text:
            slug = url.rstrip("/").split("/")[-1].replace(".html", "")
            save_document(text, f"pymapdl_{slug}.txt")

    print("Done. Raw documents saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
