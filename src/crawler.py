#!/usr/bin/env python3
import socket
import netaddr

'''
Given a list of networks or IP's find any network devices with open SSH or Telnet ports.
Do additional scan to find out if it's actually a network switch.
Populate a database with IP addresses (perhaps other metadata) of extant switches.
'''

def check_for_method(network_list):
    # Work through the range testing for tcp/22 access
    # Return a list of IP's with access or "none".
    for line in network_list:
        try:
            _network = netaddr.IPNetwork(line.rstrip())
        except netaddr.core.AddrFormatError as notIp:
            # The line contained something other than an ip or CIDR formatted address
            print("WARNING: " + str(notIp))
            continue
        for address in _network.iter_hosts():
            try:
                ssh_sock = socket.create_connection((str(address), '22'), timeout=1)
                print(str(address) + " ssh")
            except socket.timeout as timeout:
                continue
            except OSError:#This means the system rejected a connection to tcp/22
                try:
                    telnet_sock = socket.create_connection((str(address), '23'), timeout=1)
                    print(str(address) + " telnet")
                except socket.timeout:
                    continue
            except Exception as e:
                print(e)

def main():
    network_list = open('networks.csv', 'r')
    # Each line is a network in CIDR format or a single IP address.
    host_methods = check_for_method(network_list)

if __name__ == "__main__":
    main()
