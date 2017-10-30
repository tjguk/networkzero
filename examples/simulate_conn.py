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

def available_ints():
    '''Use netifaces to create a list of interfaces and their properties.
    '''
    local_ints = netifaces.interfaces()
    return [netifaces.ifaddress(interface) for interface in local_ints] 


def is_interface_valid(interface):
    address = interface.get('addr', '')
    try:
        return address.is_private(address)
    except ipaddress.AddressValueError:
        return False


def find_rfc1918(list_of_interfaces):
    for int_dict in list_of_interfaces:
        for nested_dict in int_dict:
            try:
                if ipaddress.IPv4Address(int_dict[nested_dict][0]['addr']).is_private():
                    print("Your address is most likely: {}".format(int_dict[nested_dict][0]['addr']))
            except:
                pass


'''
address = nw0.advertise("hello", "10.183.204.55")
print(local_ints)
sys.exit(255)
while True:
    name = nw0.wait_for_message_from(address)
    nw0.send_reply_to(address, "Hello " + name)
'''

def main():
    local_i = available_ints()
    print(local_i)
    find_rfc1918(local_i)
    pdb.set_trace()
if __name__ == "__main__":
    main()
