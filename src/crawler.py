#!/usr/bin/env python3

'''
Given a list of networks or IP's find any network devices with open SSH or Telnet ports.
Do additional scan to find out if it's actually a network switch.
Populate a database with IP addresses (perhaps other metadata) of extant switches.
'''

def get_list():
    try:
        with open('networks.csv') as networks:
            _network_list = networks.read()
            return _network_list
    except Exception as e:
        pass

def check_for_ssh(network):
    # Work through the range testing for tcp/22 access
    # Return a list of IP's with access or "none".
    pass

def main():
    network_list = get_list()
    # Each line is a network in CIDR format or a single IP address.
    ssh_ips = check_for_ssh(network)

if __name__ == "__main__":
    main()
