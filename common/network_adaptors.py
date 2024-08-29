import psutil


def get_adaptors():
    nets = psutil.net_if_addrs()
    print(nets)
    adaptors = {
        key: address.address for key, snicaddrs in nets.items()
        for address in snicaddrs if address.family in (2,)
    }

    return adaptors


# adaptors = get_adaptors()
# print(adaptors)
