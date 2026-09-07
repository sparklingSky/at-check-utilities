import concurrent.futures
import time
from pathlib import Path

import keyring
import requests
from tqdm import tqdm

from auxiliary.ip_sorting import ipv4_ipv6_sort
from auxiliary.ip_validator import ip_validator

virusTotalUrlStart = "https://www.virustotal.com/gui/ip-address/"
virusTotalUrlEnd = "/detection/"

try:
    api_key = keyring.get_password(
        service_name="virustotal", username="virustotal_api_user"
    )
except:
    raise ValueError("VirusTotal API key not found.")

api_headers = {"x-apikey": api_key, "accept": "application/json"}

BASE_DIR = Path(__file__).parent
input_file = BASE_DIR / "mbl_input_ips.txt"
output_bl_file = BASE_DIR / "mbl_listed_ips.txt"
output_cl_file = BASE_DIR / "mbl_clean_ips.txt"


def check_single_ip(ip):
    # 4 lookups per min, 500 lookups per day, 15.5 K lookups per month - with a public API key
    # if using Premium API, change the limits according to your licensed service step
    status = 0  # 0 for clean, 1 for blacklisted
    try:
        listing = {
            "malicious": 0,
            "suspicious": 0,
            "undetected": 0,
            "harmless": 0,
            "timeout": 0,
        }

        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        response = requests.get(url, headers=api_headers)

        json_parsed = response.json()["data"]["attributes"]["last_analysis_results"]
        malicious = ""
        suspicious = ""
        for category in listing:
            for k, v in json_parsed.items():
                if v["category"] == category:
                    listing[category] += 1
                    if v["category"] == "malicious":
                        malicious += f"{k}: {v['result']} | "
                    elif v["category"] == "suspicious":
                        suspicious += f"{k}: ({v['result']}) | "
            if category == "malicious" and listing[category] > 0:
                listing[category] = f"{listing[category]} [{malicious.rstrip(' | ')}]"
                status = 1

            elif category == "suspicious" and listing[category] > 0:
                listing[category] = f"{listing[category]} [{suspicious.rstrip(' | ')}]"
                status = 1

        listing_result = ", ".join(f"{k}: {v}" for k, v in listing.items())

    except requests.exceptions.RequestException as e:
        listing_result = f"Failed to check. Error code: {e.response.status_code}"

    finally:
        time.sleep(60)

    return {
        "ip": ip,
        "status": status,
        "listing": listing_result,
        "url": f"{virusTotalUrlStart}{ip}{virusTotalUrlEnd}",
    }


def mbl_check():
    ip_input = read_file()
    if not ip_input:
        return
    ip_count = len(ip_input)
    blacklisted = []
    clean = []

    with tqdm(total=ip_count) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(check_single_ip, arg): arg for arg in ip_input}
            for future in concurrent.futures.as_completed(futures):
                if future.result()["status"] == 1:
                    blacklisted.append(future.result())
                elif future.result()["status"] == 0:
                    clean.append(future.result())
                pbar.update(1)

    if blacklisted:
        write_results(blacklisted, output_bl_file)
    if clean:
        write_results(clean, output_cl_file)


def read_file():
    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        return []

    with open(input_file, "r", encoding="utf-8") as f:
        ips = ipv4_ipv6_sort(ip_validator(f.read()))

    if not ips:
        print("No IP addresses found to check.")
        return []

    return ips


def write_results(listing, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(
            f"{item['ip']}\n{item['listing']}\n{item['url']}\n\n" for item in listing
        )
    print(f"Completed. See the result in {filename}")


if __name__ == "__main__":
    mbl_check()
