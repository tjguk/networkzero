import os, sys
import netifaces

def get_ip4_broadcast_addresses():
    broadcast_addresses = []
    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        for family in ifaddresses:
            if family == netifaces.AF_INET:
                address_info = ifaddresses[family]
                for info in address_info:
                    if "broadcast" in info:
                        broadcast_addresses.append(info['broadcast'])
    
    return broadcast_addresses

def dump_addresses():
    for interface in netifaces.interfaces():
        print(interface)
        ifaddresses = netifaces.ifaddresses(interface)
        for family in ifaddresses:
            print("  ", netifaces.address_families[family])
            address_info = ifaddresses[family]
            for info in address_info:
                print("    ", info)

if __name__ == '__main__':
    print(dump_addresses())
