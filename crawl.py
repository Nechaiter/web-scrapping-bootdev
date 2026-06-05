from urllib.parse import urlparse
#https://docs.python.org/3/library/urllib.parse.html
from bs4 import BeautifulSoup, Tag
#https://www.crummy.com/software/BeautifulSoup/bs4/doc/

def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)
    full_path = f"{parsed_url.netloc}{parsed_url.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html,"html.parser")
    heading = soup.find(["h1","h2"])
    if isinstance(heading,Tag):
        return heading.get_text(strip=True)
    return ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html,"html.parser")
    paragraph = soup.find("main").find("p")
    if isinstance(paragraph,Tag):
        return paragraph.get_text(strip=True)
    return ""

def get_urls_from_html(html, base_url):
    pass