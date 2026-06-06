from urllib.parse import urlparse, ParseResult
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
    main = soup.find("main")
    if main is None:  # Check if main exists first
        return ""
    paragraph = main.find("p")
    if isinstance(paragraph,Tag):
        return paragraph.get_text(strip=True)
    return ""


def absolute_url_from_tags(parsed_url: ParseResult,base_url:str='')->str:
    normalized=""
    base_url=base_url.strip().rstrip("/")
    
    # Is relative:
    if parsed_url.netloc == '' or parsed_url.scheme == '':
        if parsed_url.path == "":
            return normalized

        normalized=f'{base_url}/{parsed_url.path.lstrip("./")}'
    else:
        normalized=f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'


    return normalized


def get_urls_from_html(html, base_url) -> list[str]:
    soup = BeautifulSoup(html,"html.parser")
    a_tags = soup.find_all("a")
    links: list[str] =[]

    for tag in a_tags:
        if not isinstance(tag,Tag):
            links.append("")
            continue

        href=tag.attrs.get("href")
        if not isinstance(href,str):
            links.append("")
            continue

        parsed_url=urlparse(href) 
        links.append(absolute_url_from_tags(parsed_url,base_url))
    return links

def get_images_from_html(html, base_url) -> list[str]:
    soup = BeautifulSoup(html,"html.parser")
    a_tags = soup.find_all("img")
    links: list[str] =[]

    for tag in a_tags:

        if not isinstance(tag,Tag):
            links.append("")
            continue
        src=tag.attrs.get("src")
        if not isinstance(src,str):
            links.append("")
            continue

        parsed_url=urlparse(src) 
        links.append(absolute_url_from_tags(parsed_url,base_url))
        
    return links
