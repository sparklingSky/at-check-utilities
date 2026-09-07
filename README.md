### mbl-check

Check the list of IP addresses or subnet(s) via VirusTotal API and output 
the status of the IP address if it is detected by at least one security vendor.

### sbl-check

Check the list of IP addresses or subnet(s) through the spam blacklists 
(Spamhaus, CBL, SpamCop, SORBS, Barracuda, McAfee, etc.) 
and output the status of the IP address if it is blacklisted.

### url-check

Process the list of links to the files and only output links of available files, 
discarding those that were already removed.

### auxiliary
Helper scripts used in mbl-check, sbl-check, url-check.

> [!IMPORTANT]
> 
> Before using **mbl-check**, set your VirusTotal API Key in [api_init_config.py](api_init_config.py) and run the script.
