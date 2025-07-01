import requests
from bs4 import BeautifulSoup
import json
import os
import time
import string
from tqdm import tqdm

BASE_URL = "https://www.mayoclinic.org"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_disease_links_by_letter(letter):
    """
    Scrapes all valid disease-condition URLs from the Mayo Clinic's index page for a given alphabet letter.

    Args:
        letter (str): A single uppercase character from A-Z.

    Returns:
        set: A set of filtered and valid disease-condition URLs.
    """
    url = f"{BASE_URL}/diseases-conditions/index?letter={letter}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    links = set()
    for ul in soup.find_all("ul"):
        for li in ul.find_all("li"):
            link_div = li.find("div", class_="cmp-link")
            if not link_div:
                continue

            a_tag = link_div.find("a", href=True)
            if not a_tag:
                continue

            classes = a_tag.get("class", [])
            href = a_tag["href"]
            full_url = href if href.startswith("http") else BASE_URL + href

            if (
                "cmp-button__link" in classes and
                "cmp-back-to-top" not in classes and
                "/diseases-conditions/" in full_url and
                "/symptoms-causes/" in full_url and
                "syc-" in full_url
            ):
                links.add(full_url)

    return links


def scrape_condition_page(url):
    """
    Extracts the condition title and sectioned paragraph content from a condition detail page.

    Args:
        url (str): URL of the Mayo Clinic condition article.

    Returns:
        dict: A structured dictionary with title, content, URL, source, and category.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Unknown Title"
        sections = []

        for h2 in soup.find_all("h2"):
            section_title = h2.get_text(strip=True)
            paragraphs = [
                p.get_text(strip=True)
                for p in h2.find_next_siblings()
                if p.name == "p" and p.get_text(strip=True)
            ]
            if paragraphs:
                section = f"{section_title}\n" + "\n".join(paragraphs)
                sections.append(section)

        return {
            "title": title,
            "content": "\n\n".join(sections),
            "url": url,
            "source": "Mayo Clinic",
            "category": "Health Condition"
        }

    except:
        return None


def save_json(data, filepath):
    """
    Saves Python data to a JSON file with pretty formatting.

    Args:
        data (object): Any JSON-serializable data.
        filepath (str): Output file path.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """
    Main controller function:
    - Collects condition links A-Z
    - Scrapes details from each link
    - Saves both link list and full scraped data to disk
    """
    os.makedirs("data", exist_ok=True)
    all_links = set()

    print(" Collecting condition links A-Z...")
    for letter in tqdm(string.ascii_uppercase, desc="Fetching index pages"):
        try:
            all_links.update(get_disease_links_by_letter(letter))
        except:
            continue
        time.sleep(1) 

    save_json(sorted(all_links), "data/mayo_condition_links.json")
    print(f"Saved {len(all_links)} links to mayo_condition_links.json")

    print("\n Scraping each condition page...")
    all_conditions = []
    for url in tqdm(sorted(all_links), desc="Scraping condition pages"):
        data = scrape_condition_page(url)
        if data:
            all_conditions.append(data)
        time.sleep(0.5)

    save_json(all_conditions, "data/mayo_conditions.json")
    print(f"Saved full condition data to mayo_conditions.json")


if __name__ == "__main__":
    main()