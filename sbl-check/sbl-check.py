import concurrent.futures
import random
import re
import time
from pathlib import Path

import dns.exception
import dns.resolver
from tqdm import tqdm

from auxiliary.ip_sorting import ipv4_ipv6_sort
from auxiliary.ip_validator import ip_validator

BASE_DIR = Path(__file__).parent
input_file = BASE_DIR / "sbl_input_ips.txt"
output_bl_file = BASE_DIR / "sbl_listed_ips.txt"
output_cl_file = BASE_DIR / "sbl_clean_ips.txt"
output_und_file = BASE_DIR / "sbl_undefined_ips.txt"


blacklists = [
    "aspews.ext.sorbs.net",
    "b.barracudacentral.org",
    "l1.bbfh.ext.sorbs.net",
    "l2.bbfh.ext.sorbs.net",
    "l3.bbfh.ext.sorbs.net",
    "l4.bbfh.ext.sorbs.net",
    "cbl.abuseat.org",
    "cidr.bl.mcafee.com",
    "dnsbl.sorbs.net",
    "problems.dnsbl.sorbs.net",
    "proxies.dnsbl.sorbs.net",
    "relays.dnsbl.sorbs.net",
    "safe.dnsbl.sorbs.net",
    "dul.dnsbl.sorbs.net",
    "rhsbl.sorbs.net",
    "badconf.rhsbl.sorbs.net",
    "nomail.rhsbl.sorbs.net",
    "zombie.dnsbl.sorbs.net",
    "block.dnsbl.sorbs.net",
    "escalations.dnsbl.sorbs.net",
    "http.dnsbl.sorbs.net",
    "misc.dnsbl.sorbs.net",
    "smtp.dnsbl.sorbs.net",
    "socks.dnsbl.sorbs.net",
    "spam.dnsbl.sorbs.net",
    "recent.spam.dnsbl.sorbs.net",
    "new.spam.dnsbl.sorbs.net",
    "old.spam.dnsbl.sorbs.net",
    "web.dnsbl.sorbs.net",
    "bl.spamcop.net",
    "pbl.spamhaus.org",
    "sbl.spamhaus.org",
    "sbl-xbl.spamhaus.org",
    "xbl.spamhaus.org",
    "zen.spamhaus.org",
    "multi.surbl.org",
    "dnsbl-0.uceprotect.net",
    "dnsbl-1.uceprotect.net",
    "dnsbl-2.uceprotect.net",
    "dnsbl-3.uceprotect.net",
    "bl.blocklist.de",
]

delay = random.uniform(0.5, 1)


def check_single_ip(ip):
    listing = []
    octets = ip.split(".")
    reversed_ip = ".".join(reversed(octets))

    for blacklist in blacklists:
        try:
            response = dns.resolver.resolve(f"{reversed_ip}.{blacklist}", "A")
            for rdata in response:
                if rdata.address == "127.0.0.2":
                    listing.append(f"{blacklist} (listed)")

        except dns.resolver.NXDOMAIN:
            pass

        except dns.resolver.NoNameservers:
            listing.append(f"{blacklist} (no nameservers)")

        except (dns.resolver.LifetimeTimeout, dns.resolver.Timeout):
            listing.append(f"{blacklist} (timeout)")

        except dns.resolver.NoAnswer:
            listing.append(f"{blacklist} (no response)")

    blacklisted = sorted(listing, key=lambda x: re.search(r"\((.*?)\)", x).group(1))
    blacklisted = ", ".join(blacklisted)

    time.sleep(delay)
    return ip, blacklisted


def sbl_check():
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
                if future.result()[1]:
                    blacklisted.append(future.result())
                else:
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
        for item in listing:
            if item[1]:
                f.write(f"{item[0]}\n{item[1]}\n\n")
            else:
                f.write(f"{item[0]}\n")
    print(f"Completed. See the result in {filename}")


if __name__ == "__main__":
    sbl_check()
