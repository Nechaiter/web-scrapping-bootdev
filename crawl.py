from urllib.parse import urlparse, ParseResult
#https://docs.python.org/3/library/urllib.parse.html
from bs4 import BeautifulSoup, Tag 
#https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from typing import TypedDict
#type hint for dict
import requests


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
    soup = BeautifulSoup(html, "html.parser")

    main_section = soup.find("main")
    first_p = soup.find("p")
    if isinstance(main_section, Tag):
        p_in_main = main_section.find("p")
        if isinstance(p_in_main, Tag):
            first_p=p_in_main
    
        

    return first_p.get_text(strip=True) if isinstance(first_p, Tag) else ""


def absolute_url_from_tags(parsed_url: ParseResult,base_url:str='')->str:
    normalized=""

    base_parsed=urlparse(base_url.strip().rstrip("/"))
    print(10*"-")
    print(base_parsed)
    print(parsed_url)
    print(10*"-")

    # Is relative:
    if parsed_url.netloc == '' or parsed_url.scheme == '':
        
        if parsed_url.path == "":
            return base_url

        if parsed_url.path == base_parsed.path:
            return base_url.lstrip("/")

        normalized=f'{base_url}/{parsed_url.path.lstrip("./")}'
    
    else:
        if parsed_url.scheme != "":
            normalized=f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
        else:
            normalized=f'https://{parsed_url.netloc}{parsed_url.path}'
            

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




class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def extract_page_data(html: str, page_url: str)->PageData:
    data = {
        "url":page_url,
        "heading":get_heading_from_html(html),
        "first_paragraph":get_first_paragraph_from_html(html),
        "outgoing_links":get_urls_from_html(html,page_url),
        "image_urls":get_images_from_html(html,page_url)
    }
    return data

def get_html(url:str)->str:
    try:
        response = requests.get(url,headers={"User-agent":"BootCrawler/1.0"})
        response.raise_for_status()

        if response.headers["Content-type"] != "text/html":
            raise requests.exceptions.InvalidHeader
    
    except requests.exceptions.HTTPError:
        print("http error") 

    except requests.exceptions.InvalidHeader:
        print("not a text/html header")
    except Exception as e:
        print(e)
    

    return response.text


def crawl_page(base_url, current_url=None, page_data:dict={}):
    if urlparse(base_url).netloc != urlparse(current_url).netloc:
        return
    current_normalized = normalize_url(current_url)
    if current_normalized in page_data:
        return
    
    html=get_html(current_normalized)
    if not isinstance(html,str):
        return
    
    data:PageData=extract_page_data(html,current_normalized)
    print(current_normalized)
    page_data[current_normalized]=data
    for link in data["outgoing_links"]:
        crawl_page(base_url,link,page_data)

    return page_data



def run(url)->None:
    data = crawl_page(url,url)
    print(f"There were {len(data)} links fetchs")
