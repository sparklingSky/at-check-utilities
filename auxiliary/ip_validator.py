import ipaddress
import re


def ip_validator(input_data):
    """
    :param input_data: string of IP addresses or subnet(s)
    :return: formatted list of IP addresses
    """
    if not input_data:
        return []

    formatted_input_data = re.findall(r"[^\s,\[\]\'\"]+", input_data)

    for item in formatted_input_data:
        try:
            # strict=False allows to pass a subnet with a CIDR mask, e.g. 185.95.23.1/29
            ipaddress.ip_network(item, strict=False)
        except ValueError:
            pass

    formatted_ip_list = []
    for item in formatted_input_data:
        try:
            network = ipaddress.ip_network(item, strict=False)
            formatted_ip_list.extend(str(ip) for ip in network)
        except ValueError:
            pass

    if len(formatted_ip_list) == 0:
        return None
    return formatted_ip_list
