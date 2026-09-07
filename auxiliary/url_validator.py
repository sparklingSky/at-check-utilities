def url_validator(urls):
    formatted_urls = [url for url in urls.split() if "http" in url]
    formatted_urls = list(set(formatted_urls))
    if len(formatted_urls) == 0:
        return None
    return formatted_urls
