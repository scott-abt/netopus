#!/usr/bin/env python3
import socket
import netaddr

'''
Given a list of networks or IP's find any network devices with open SSH or Telnet ports.
Do additional scan to find out if it's actually a network switch.
Populate a database with IP addresses (perhaps other metadata) of extant switches.
'''

def check_for_ssh(network_list):
    # Work through the range testing for tcp/22 access
    # Return a list of IP's with access or "none".
    for line in network_list:
        # Need to break up networks and try each node.
        _network = netaddr.IPNetwork(line.rstrip())
        for address in _network.iter_hosts():
            try:
                print("Trying " + str(address))
                sock = socket.create_connection((str(address), '22'), timeout=3)
            except socket.timeout as timeout:
                print("Connection to " + str(address) + " timed out.")

def main():
    network_list = open('networks.csv', 'r')
    # Each line is a network in CIDR format or a single IP address.
    ssh_ips = check_for_ssh(network_list)

if __name__ == "__main__":
    main()
