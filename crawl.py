#https://docs.python.org/3/library/urllib.parse.html
#https://www.crummy.com/software/BeautifulSoup/bs4/doc/



from typing import TypedDict
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup, Tag
import requests

import asyncio
import aiohttp

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def normalize_url(url: str) -> str:
    parsed_url = urlparse(url)
    full_path = f"{parsed_url.netloc}{parsed_url.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    main_section = soup.find("main")
    if isinstance(main_section, Tag):
        first_p = main_section.find("p")
    else:
        first_p = soup.find("p")

    return first_p.get_text(strip=True) if isinstance(first_p, Tag) else ""

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    urls = []
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all("a")

    for anchor in anchors:
        if not isinstance(anchor, Tag):
            continue
        href = anchor.get("href")
        if isinstance(href, str) and href:
            try:
                absolute_url = urljoin(base_url, href)
                urls.append(absolute_url)
            except Exception as e:
                print(f"{str(e)}: {href}")

    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    image_urls = []
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")

    for img in images:
        if not isinstance(img, Tag):
            continue
        src = img.get("src")
        if isinstance(src, str) and src:
            try:
                absolute_url = urljoin(base_url, src)
                image_urls.append(absolute_url)
            except Exception as e:
                print(f"{str(e)}: {src}")

    return image_urls


def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


def crawl_page(
    base_url: str,
    current_url: str | None = None,
    page_data: dict[str, PageData] | None = None,
) -> dict[str, PageData]:
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    base_url_obj = urlparse(base_url)
    current_url_obj = urlparse(current_url)
    #if the domain is not from the orginal base, we skip
    if current_url_obj.netloc != base_url_obj.netloc:
        return page_data

    normalized_url = normalize_url(current_url)

    if normalized_url in page_data:
        return page_data

    print(f"crawling {current_url}")
    html = safe_get_html(current_url)
    if html is None:
        return page_data

    page_info = extract_page_data(html, current_url)
    page_data[normalized_url] = page_info

    next_urls = get_urls_from_html(html, base_url)
    for next_url in next_urls:
        page_data = crawl_page(base_url, next_url, page_data)

    return page_data


def get_html(url: str) -> str:
    try:
        response = requests.get(url)
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")

    if response.status_code > 399:
        raise Exception(f"got HTTP error: {response.status_code} {response.reason}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"got non-HTML response: {content_type}")

    return response.text


def safe_get_html(url: str) -> str | None:
    try:
        return get_html(url)
    except Exception as e:
        print(f"{e}")
        return None


#  asyncio.Lock is use to prevent race conditions, remember that some I/O operations are truly parallel
# if we are doing an async operation who writes a file, it doesnt matter if we use the await keyword, the function
# gonna wait his logic, but other coroutines can open the file and write while the previus operation is still running


# asyncio.Semaphore limits how many coroutines can be running

#aiohttp integrates the http request with asyncio, we cant use request with asyncio / (or delegate the requests in another thread)

class AsyncCrawler():
    def __init__(self,base_url,max_concurrency,max_pages) -> None:
        self.base_url: str=base_url
        self.base_domain: str = urlparse(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.lock: asyncio.Lock = asyncio.Lock()
        self.max_concurrency: int = max_concurrency # States how many coroutines will be
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrency) # Actually limits the coroutines
        self.session: aiohttp.ClientSession
        self.seen: set[str] = set()
        self.max_pages:int=max_pages
        self.all_tasks: set[asyncio.Task] = set() # Tasks that we want to stop
        self.should_stop: bool = False


    # Methods to open and close an aiohttp client session

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):

        async with self.lock:
            if self.should_stop:
                return False

            if self.max_pages <= len(self.seen):
                self.should_stop=True
                print("Reached maximum number of pages to crawl.")

                # If we cancel, current task dont have the time to save their data
                #for task in self.all_tasks:
                #    task.cancel()
                return False
            

            if normalized_url in self.seen:
                return False
            self.seen.add(normalized_url)
            return True

    async def get_html(self, url: str) -> str|None:
        
        try:
            async with self.session.get(url) as response:
                if response.status > 399:
                    print(f"got HTTP error: {response.status} {response.reason}")
                    return None

                content_type = response.headers.get("content-type", "")
                
                if "text/html" not in content_type:
                    print(f"got non-HTML response: {content_type}")
                    return None

                return await response.text()    
        except Exception as e:
            print(f"network error while fetching {url}: {e}")
            return None;

        
    async def crawl_page(self,
    current_url: str) -> None:
        if self.should_stop:
            return
        current_url_obj = urlparse(current_url)
        #if the domain is not from the orginal base, we skip
        if current_url_obj.netloc != self.base_domain:
            return None

        normalized_url=normalize_url(current_url)

        if not await self.add_page_visit(normalized_url):
            return None
        
        print(f"crawling {current_url}")

        # Fetch restriccion to prevent ip bans
        async with self.semaphore:
            html = await self.get_html(current_url)
        
        if html is None:
            return None
        
        async with self.lock:
            self.page_data[normalized_url] = extract_page_data(html, current_url)

        next_urls = get_urls_from_html(html, self.base_url)
        tasks=[]
        for next_url in next_urls:
            task=asyncio.create_task(self.crawl_page(next_url))
            tasks.append(task)
            self.all_tasks.add(task)

        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass

        
        for task in tasks:
            self.all_tasks.discard(task)
            


    async def crawl(self)->dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data
    


async def crawl_site_async(url:str,max_concurrency:int,max_pages:int)->dict[str, PageData]:
    async with AsyncCrawler(url,max_concurrency,max_pages) as crawl:
        return await crawl.crawl()
    


