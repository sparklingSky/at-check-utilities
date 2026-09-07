import concurrent.futures
import time
from pathlib import Path

import requests
from tqdm import tqdm

from auxiliary.url_validator import url_validator

BASE_DIR = Path(__file__).parent
input_file = BASE_DIR / "input_urls.txt"
output_file = BASE_DIR / "available_urls.txt"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
}

keywords = [
    "Removed for Copyright Infringement",
    "Not found",
    "No file",
    "404 error page",
    "No file(s) found",
    "THIS FILE WAS DELETED",
    "does not exist",
    "file was removed",
    "No results containing all your search terms were found",
    "This video is no longer available due to a copyright claim",
    "nothing found",
    "File no longer available",
    "file was not found",
    "This folder is no longer available",
    "removed due to DMCA Complaint",
    "Links have been permanently deleted",
    "Datei wurde wegen Urheberrechtsverletzung gelöscht",
    "Removed for DMCA",
    "Channel Banned",
    "dit bestand bestaat niet",
    "Links have been permanently deleted",
    "abuse removed",
    "this link to book was deleted",
    "File no longer available",
    "the file link that you requested is not valid",
    "cannot be found",
    "file removed",
    "no results found",
    "has been deleted",
    "bestand niet beschikbaar",
    "could not find any files",
    "link was deleted",
    "file is blocked",
    "page has been blocked",
    "file does not exist",
    "No files found",
    "File not found",
    "Link already expired",
    "file has been deleted",
    "Page not found",
    "file-not-found",
    "No links to show",
    "No related files",
    "file was deleted",
    "file is no longer available",
    "File not available",
    "content was removed",
    "file is not found",
    "Folder can not be found",
]


def check_single_url(url):
    time.sleep(0.05)
    print(url)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code >= 400:
            return 0
        if not any(phrase in response.text for phrase in keywords):
            return 1
    except requests.RequestException:
        return 0


def check_urls(parsed_input):
    input_count = len(parsed_input)

    with tqdm(total=input_count) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {
                executor.submit(check_single_url, arg): arg for arg in parsed_input
            }
            results = []
            for future in concurrent.futures.as_completed(futures):
                if future.result() == 1:
                    results.append(futures[future])
                pbar.update(1)

    write_results(results)


def parse_urls():
    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        return []

    with open(input_file, "r", encoding="utf-8") as f:
        urls = url_validator(f.read())

    if not urls:
        print("No URLs found to check.")
        return []

    return urls


def write_results(available_urls):
    with open(output_file, "w", encoding="utf-8") as f:
        if not available_urls:
            f.write("Congrats! There're no available files.\n")
        else:
            f.writelines(f"{url}\n" for url in available_urls)


if __name__ == "__main__":
    urls_to_check = parse_urls()
    if urls_to_check:
        check_urls(urls_to_check)
