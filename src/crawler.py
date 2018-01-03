#!/usr/bin/env python3
import socket
import netaddr
import sqlite3
import getpass
from paramiko.client import SSHClient, AutoAddPolicy

'''
Given a list of networks or IP's find any network devices with open SSH or Telnet ports.
Do additional scan to find out if it's actually a network switch.
Populate a database with IP addresses (perhaps other metadata) of extant switches.
'''

def get_cursor():
    try:
        _conn = sqlite3.connect("live_hosts.db")
        _curs = _conn.cursor()
        return(_curs)
    except Exception as e:
        print(e)

def get_metadata(addy, port):
    try:
        _curs = get_cursor()
        _result = _curs.execute("SELECT hostname, method FROM hosts WHERE address = '{}' AND active = '1'".format(addy))
        _row = _result.fetchone()
        return(_row)
    except Exception as e:
        print(e)

def compare_config(config, addy):
    config_file = open(str(addy) + '.cfg', 'w')
    for line in config:
        config_file.write(line)
    config_file.close()
    # This works, but need to use version control for versioning now

def connect_to_ssh(addy):
    username = input("Username: ")
    password = getpass.getpass()
    ''' do a session and get info'''
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy)
    client.connect(str(addy), 22, username=username, password=password)
    output = client.exec_command('show configuration|no-more')
    config = output[1].readlines()
    #Works for juniper... don't print it, save to file after diff
    compare_config(config, addy)
    
def check_existing(addy, port):
    try:
        _curs = get_cursor()
        _curs.execute("SELECT COUNT(*) FROM hosts WHERE address = '{}' AND active = '1'".format(addy))

        if _curs.fetchone()[0] > 0:
            '''There is an existing row for this IP.
            * update the last seen, configured device hostname (not the resolved dns)
            * make sure the method is correct.
            '''
            hostname, method = get_metadata(addy, port)
            '''
            Connect to the device with paramiko
            compare metadata with configured hostname
            '''
            if method == 'ssh':
                connect_to_ssh(addy)
            else:
                print("Do a telnet instead")
            return 1
        else:
            #insert new row
            return 0
    except Exception as e:
        print(e)

def crawl(network_list):
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
                exists = check_existing(address, 22)
            except socket.timeout as timeout:
                continue
            except OSError:#This means the system rejected a connection to tcp/22
                try:
                    telnet_sock = socket.create_connection((str(address), '23'), timeout=1)
                    exists = check_existing(address, 23)
                except socket.timeout:
                    continue
            except Exception as e:
                print(e)

def main():
    network_list = open('networks.csv', 'r')
    # Each line is a network in CIDR format or a single IP address.
    crawl(network_list)

if __name__ == "__main__":
    main()
