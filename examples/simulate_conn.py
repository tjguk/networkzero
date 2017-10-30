import networkzero as nw0
import netifaces
import sys
import ipaddress
import pdb

'''
A script that will select the most likely IP address to bind to when running the server/beacon.
Use the netifaces method and select the RFC1918 IPv4 address assigned to an interface.
The idea is to simplify troubleshooting.
'''

def available_addresses():
    '''Use netifaces to create a list of interfaces and their properties.
    '''
    v4_addresses = []
    local_ints = netifaces.interfaces()
    local_int_addresses = [netifaces.ifaddresses(interface) for interface in local_ints]
    for interface in local_int_addresses:
        try:
            v4_addresses.extend(interface[netifaces.AF_INET])
        except KeyError:
            pass
    return v4_addresses
            

def find_usable_addresses(interface):
    '''Helper function to evaluate valid RFC1918 addresses.
    '''
    for address in interface:
        address_string = address.get('addr', '')
        try:
            v4_address = ipaddress.IPv4Address(address_string)
        except ipaddress.AddressValueError:
            pass
        else:
            if v4_address.is_private and not v4_address.is_loopback and not v4_address.is_link_local:
                yield address_string


#def find_rfc1918(list_of_addresses):
#    valid_interfaces = valid_addresses(list_of_interfaces)
#    return [interface['addr'] for interface in valid_interfaces]


def start_server(address):
    address = nw0.advertise("hello", address)
    while True:
        name = nw0.wait_for_message_from(address)
        nw0.send_reply_to(address, "Hello " + name)

'''
address = nw0.advertise("hello", "10.183.204.55")
print(local_ints)
sys.exit(255)
while True:
    name = nw0.wait_for_message_from(address)
    nw0.send_reply_to(address, "Hello " + name)
'''

def main():
    local_i = available_addresses()
    print(local_i)
    server_address = (list(find_usable_addresses(local_i)))
    start_server(server_address[0])

if __name__ == "__main__":
    main()
