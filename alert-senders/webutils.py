import netifaces
import ipaddress


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        ))


def local_mac_for_remote_ip(remote_ip):
    """Finds the MAC address of the interface in the same network as the given remote IP address."""
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        try:
            interface_mac = addresses[netifaces.AF_LINK][0]['addr']
            interface_ip_info = addresses[netifaces.AF_INET][0]
            interface_network = ipaddress.ip_network(interface_ip_info['addr'] + "/" + interface_ip_info['netmask'], False)
        except (IndexError, KeyError):
            # Ignore interfaces with missing IP info.
            continue
        if ipaddress.ip_address(remote_ip) in interface_network:
            return interface_mac
    return ""
