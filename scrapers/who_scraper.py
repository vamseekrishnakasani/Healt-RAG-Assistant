import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.who.int"
FACT_SHEET_URL = "https://www.who.int/news-room/fact-sheets"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_fact_sheet_links():
    """Scrape article links from WHO alphabetical fact sheet list."""
    response = requests.get(FACT_SHEET_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    container = soup.find("ul", {"id": "alphabetical-nav-filter"})
    links = []

    if container:
        for tag in container.find_all("a", href=True):
            href = tag['href']
            if href.startswith("/news-room/fact-sheets/detail/"):
                full_url = BASE_URL + href
                links.append(full_url)

    return list(set(links))  # remove duplicates


def scrape_article(url):
    """Extract title and full content from a WHO fact sheet article page."""
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else "No Title"

    # Robust content extraction: paragraphs, subheadings, lists
    content_container = soup.find("article", class_="sf-detail-body-wrapper")
    if not content_container:
        return {"title": title_text, "content": "", "url": url, "source": "WHO", "category": "Fact Sheet"}

    parts = []
    for tag in content_container.find_all(["h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if text:
            parts.append(text)

    content = "\n".join(parts)

    return {
        "title": title_text,
        "content": content,
        "url": url,
        "source": "WHO",
        "category": "Fact Sheet"
    }

def main():
    print("Scraping WHO Fact Sheet links...")
    links = get_fact_sheet_links()
    print(f"Found {len(links)} articles")

    all_articles = []

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}] Scraping: {link}")
        try:
            article = scrape_article(link)
            if len(article['content']) > 100:
                all_articles.append(article)
        except Exception as e:
            print(f"Error scraping {link}: {e}")
        time.sleep(1)

    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    # Save to data/who_facts.json
    output_path = "data/who_facts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_articles)} articles to {output_path}")


if __name__ == "__main__":
    main()