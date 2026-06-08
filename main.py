import sys
from crawl import crawl_page, crawl_site_async
import asyncio
import time
def main() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no website provided")
        sys.exit(1)
    if len(args) > 2:
        print("too many arguments provided")
        sys.exit(1)

    base_url = args[1]

    print(f"starting crawl of: {base_url}...")

    page_data = crawl_page(base_url)

    print(f"Found {len(page_data)} pages:")
    for page in page_data.values():
        print(f"- {page['url']}: {len(page['outgoing_links'])} outgoing links")

    sys.exit(0)

async def main_async() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no website provided")
        sys.exit(1)
    if len(args) > 2:
        print("too many arguments provided")
        sys.exit(1)

    base_url = args[1]

    CONCURRENCY=20
    print(f"starting crawl of: {base_url}...")
    start = time.perf_counter()
    page_data = await crawl_site_async(base_url,CONCURRENCY)
    
    print(f"Found {len(page_data)} pages:")
    for page in page_data.values():
        print(f"- {page['url']}: {len(page['outgoing_links'])} outgoing links")
    elapsed = time.perf_counter() - start
    print(f"Tiempo total: {elapsed:.2f} segundos usando un maximo de {CONCURRENCY} peticiones a la vez")

    sys.exit(0)


#3.28 , 1 peticion
# 1.38, 10 peticiones
# 1.04 20 peticiones
if __name__ == "__main__":
    #main()
    asyncio.run(main_async())
