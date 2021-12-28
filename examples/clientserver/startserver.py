'''This is a simple script to help understand client/server relationships across a network and/or help with network troubleshooting.
It uses netifaces to parse interfaces on the machine with IPv4 addresses, and validates them using the ipaddress library.
A server listening on the first valid IPv4 address is then started.
An exception is raised if no valid IPv4 addresses are found.
'''

import ipaddress
import networkzero as nw0
import netifaces



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


def start_server(address, service_name='hello'):
    '''Start a networkzero server on the address supplied, and optonally take a service name as an argument.
    Acknowledge messages sent successfully to the service.
    '''
    address = nw0.advertise(service_name, address)
    while True:
        name = nw0.wait_for_message_from(address)
        nw0.send_reply_to(address, "Hello " + name)


def main():
    local_ips = available_addresses()
    #Flatten dictionary into a list
    server_address = list(find_usable_addresses(local_ips))
    try:
        print("Starting server on IP address {}".format(server_address[0]))
        start_server(server_address[0])
    except IndexError:
        print("Couldn't find any valid RFC 1918 addresses to bind server to")


if __name__ == "__main__":
    main()
