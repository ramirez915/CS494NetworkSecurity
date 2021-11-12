import sys
from scapy.all import *

def send_packet(src_ip,dst_ip,dst_port,payload):
#	print(src_ip)
#	print(type(src_ip))
#	print(dst_ip)
#	print(type(dst_ip))
#	print(dst_port)
	dst_port = int(dst_port)
#	print(type(dst_port))
#	print(payload)
	#convert payload string to bytes
	plBytes = payload.encode()
	#make list that will contain the bytes
	bList = []
	for byte in plBytes:
		bList.append(byte)

#	print(bList)
#	print(len(bList))
	#check if the list of bytes is longer than 150 bytes
	if len(bList) > 150:
		print("too long... exiting")
		return

	#by here the payload is valid so make spoofed packet
	packet = IP(src = src_ip, dst = dst_ip)/UDP(dport = dst_port)/payload
	send(packet)
	return

#send_packet(1,1,1,"hello world whats up aasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfsasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdadsflkdjfaslkdjfklasjdfkljasdfklsajdfasdlkfjas;lkdjf");
if __name__ == "__main__":
	src_ip = str(sys.argv[1])
	dst_ip = str(sys.argv[2])
	dst_port = str(sys.argv[3])
	payload = str(sys.argv[4])
	
	send_packet(src_ip,dst_ip,dst_port,payload)
