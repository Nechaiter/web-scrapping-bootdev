from urllib.parse import urlsplit

def normalize_url(url:str)->str:
    split=urlsplit(url)
    print(split.hostname+split.path)
    parsed_url=split.hostname+split.path
    return parsed_url