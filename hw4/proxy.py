import argparse
import socket
import re
import datetime

#how many connections can be held
MAXCONN = 10

#pattern for a card number
#anyting not 0-9 then any number 0-9 4 then 4 then 4 then 4
#grouped whole expression in order to use findall and use its list and elem 0
#cardPattern = '([^0-9])([0-9]{4})-?([0-9]{4})-?([0-9]{4})-?([0-9]{4})'
cardPattern = '(([0-9]{4})-([0-9]{4})-([0-9]{4})-([0-9]{4}))'
#pattern for SSN
#anything not 0-9 but then anything 0-9 3 times then 2 then 4
#grouping everything together so that this can be looked for as a group
# so that I can then use findall and use element 0 from that list
ssnPattern = '(([0-9]{3})-([0-9]{2})-([0-9]{4}))'

#phone numbers can have one of these 3 patterns
phonePattern = '\([0-9]{3}\)[0-9]{3}\-[0-9]{4}'
phonePattern2 = '[0-9]{3}\-[0-9]{3}\-[0-9]{4}'
phonePattern3 = '\([0-9]{3}\)\-[0-9]{3}\-[0-9]{4}'


#stores the mode of the program when run
mode = None

#stores the names of the files that are to be written to
file1 = 'info_1.txt'	#passive
file2 = 'info_2.txt'	#active

#get the -m argument
def getArgs():
	parser = argparse.ArgumentParser(description= 'input -m active/passive')
	parser.add_argument('-m',help='active or passive')		#-m flag
	parser.add_argument('ip',help='ip address to listen to')	#ip
	parser.add_argument('port',help='port to listen to')		#port

	args = parser.parse_args()
	if args.ip != None:
		print('ip is ',args.ip)
	if args.port != None:
		print('port is ',args.port)

	return (args.m,args.ip,args.port)


def getMode(args):
	if args[0] == 'active':
		print('active mode')
		return 'active'

	elif args[0] == 'passive':
		print('passive mode')
		return 'passive'

	else:
		print('invalid input')
		return None

#checks if credit card pattern is detected
def checkIfCardNum(seq):
#	print('checking ',seq)
	#check the current sequence against the regular expression
	match = re.search(cardPattern,seq)
	match2 = re.findall(cardPattern,seq)

	if match == None:
		return (False,None)

	print('card numeber FOUND**********************************')
#	print(match.group())
	#print('match2',match2)
	for i in match2:
		print(i[0])
#	return (True,match.group(0))
	return (True,match2)

#checks if ssn pattern is detected
def checkIfSsn(seq):
	match = re.search(ssnPattern,seq)
	match2 = re.findall(ssnPattern,seq)

	if match == None:
		return (False,None)

	print('ssn number FOUND*******************')
#	print(match.group())
	for i in match2:
		print(i[0])
#	return (True,match.group(0))
	return (True,match2)

# checks for phone number pattern
#returns a list of numbers not touples****
def checkIfPhoneNum(seq):
	match = re.findall(phonePattern,seq)
	match = match + re.findall(phonePattern2,seq)
	match = match + re.findall(phonePattern3,seq)

	if len(match) == 0:
		print('phone match len is 0')
		return (False,None)

	print('phone number FOUND*****************')
	print(match)

	return (True,match)


#check if an email pattern is detected
'''
def checkIfEmail(seq):
	match = re.findall(emailPattern,seq)

	if match == None:
		return (False,None)

	print('email FOUND********************')

	for i in match:
		print(i[0])
	return (True,match)
'''


#writes to a file depending on the mode
def writeToFile(mode,toWrite,type):
	now = datetime.datetime.now()
	time = str(now.strftime("%m/%d/%Y_%H:%M:%S\n"))
#	print(time)
	if mode == 'passive':
		file = open(file1,'a+')
	elif mode == 'active':
		file = open(file2,'a+')

	for i in toWrite:
		#placed in for a phone number so that the
		#right information is written
		if len(i[0]) == 1:
			file.write(i + ':' + type + time)
			#break
		#else it is a llist of touples and only the first item in
		#each touple is wanted
		else:
			file.write(i[0] + ':' + type + time)
	file.close()
	return


def serverCode(ip,port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#allows for reuse of address
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

	#bind the socket
	sock.bind((ip,port))
	sock.listen(MAXCONN)

	while 1:
		conn, cliAddr = sock.accept()

		#depending on the mode is what is going to be run
		if mode == 'passive':
			passiveWorker(conn,cliAddr)
		elif mode == 'active':
			activeWorker(conn,cliAddr)
	sock.close()

# the worker function that is for the passive mode
# will only look for the pattern for cards and ssn for now
def passiveWorker(conn,addr):
	req = conn.recv(5120)
#	print("REQUEST ",req)
#	print("\n")

	decoded = req.decode()			# to get data as string
	decodedSplit = decoded.split('\n')	# to get each line of the request

	print('from list of split request')
	for i in decodedSplit:
		print(i)
		card = checkIfCardNum(i)
		ssn = checkIfSsn(i)
		phone = checkIfPhoneNum(i)
#		email = checkIfEmail(i)
		if card[0]:
			writeToFile(mode,card[1],'***CREDIT CARD***')
		if ssn[0]:
			writeToFile(mode,ssn[1],'***SSN***')
		if phone[0]:
			writeToFile(mode,phone[1],'***PHONE NUMBER***')
#		if email[0]:
#			writeToFile(mode,ssn[1],'***EMAIL***')

	print("RECVD DECODED",repr(decoded))
	print('\n')

	conn.sendall(req)


#similar to passiveWorker except that this one
#is supposed to inject but I was unable to get to this
# so it only writes to file_2.txt saying that
def activeWorker(conn,addr):
	req = conn.recv(5120)

	decoded = req.decode()
	decodedSplit = decoded.split('\n')

	writeToFile(mode,['no'],'***NOT YET IMPLEMENTED***')

	conn.sendall(req)



if __name__ == "__main__":
	args = getArgs()
	mode = getMode(args)
	#error checking for valid mode
	if mode == None:
		exit(1)

	ip = args[1]
	port = int(args[2])

	serverCode(ip,port)
