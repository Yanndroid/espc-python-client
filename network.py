import netifaces


def get_route_ip():
    gateways = netifaces.gateways()
    default_route = gateways["default"]
    return default_route[netifaces.AF_INET][0]
