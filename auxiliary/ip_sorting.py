import socket


def ipv4_ipv6_sort(ip_list):
    final_result = []
    ipv4_list = []
    ipv6_list = []
    for ip in ip_list:
        if ":" in ip:
            ipv6_list.append(ip)
        else:
            ipv4_list.append(ip)

    ipv4_mediate_result = [socket.inet_pton(socket.AF_INET, ip) for ip in ipv4_list]
    ipv4_mediate_result.sort()
    ipv4_result = [socket.inet_ntop(socket.AF_INET, ip) for ip in ipv4_mediate_result]

    ipv6_mediate_result = [socket.inet_pton(socket.AF_INET6, ip) for ip in ipv6_list]
    ipv6_mediate_result.sort()
    ipv6_result = [socket.inet_ntop(socket.AF_INET6, ip) for ip in ipv6_mediate_result]

    final_result.extend(ipv4_result)
    final_result.extend(ipv6_result)

    return final_result
