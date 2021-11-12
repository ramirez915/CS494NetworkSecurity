#Angel Ramirez

import argparse
import socket
import paramiko
import threading

MAXCONN = 10
#how many password attempts are there set for ssh?
#default is 3
MAXPASSATTEMPTS = 3
#generate the hosKey to be used
hostKey = paramiko.RSAKey.generate(2048)

#will contain all the names of the users from the file
#with the total number of attempts
#will reset the attempts upon a successful login
usernames = {}

#server interface class that will handle my
#implementation of the paramiko server
class Server(paramiko.ServerInterface):
	def __init__(self):
		self.event = threading.Event()

	def check_channel_request(self,kind,chanid):
#		print('overwritten check channel request')
		if kind == 'session':
#			print('SUCCESS chanid:',chanid)
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHINITED

	def check_auth_password(self,username,password):
		#checks who tried to log in
		checkIfValidUser(username)
		# checks if the total amount of tries is 
		if reachedAttemptLimitFor(username):
			zeroAttemptsFor(username)
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED

	def check_channel_shell_request(self,channel):
#		print('overwritten check channel shell request')
		channel.settimeout(60)	#times out the channel for x seconds
		self.event.set()
		return True

#get arguments from commandline
def getArgs():
	parser = argparse.ArgumentParser(description= 'input -p port')
	parser.add_argument('-p',help='ssh port number')

	args = parser.parse_args()
	if args.p == None:
		print('using default port 22')
		return 22	#default port

	else:
		print('using port',args.p)
		return args.p

'''
reads the usernames.txt and adds all the usernames
there into a dictionary with starting attempt to 0
'''
def setupUserDict():
	print('setting up username dictionary...')
	with open('usernames.txt') as f:
		content = f.readlines()
	f.close()
	for users in content:
		user = users[:-1]
		if usernames.get(user,-1) == -1:
			#print('adding ',user, ' with ', 0)
			usernames[user] = 0
	print('dicitonary is starting at: ',usernames)


'''
when a user has been attempted > 5 times
zero out the attempts for it
'''
def zeroAttemptsFor(selectedName):
	if usernames.get(selectedName,-1) != -1:
		print('zeroing attempts for',selectedName)
		usernames[selectedName] = 0
	else:
		print('user name does not exit...')
	print(usernames)
	return
'''
checks if the log in attempt is a valid user
if true then add
'''
def checkIfValidUser(name):
	if usernames.get(name,-1) != -1:
		print('user from list:',name)
		usernames[name] = usernames[name] + 1
		return True
	print('user not from list:',name)
	return False


'''
returns true is reached the limit of attempts
for a specific user, false if still below 5
'''
def reachedAttemptLimitFor(name):
	print('status of users:',usernames)
	if usernames.get(name,-1) != -1:
		if usernames[name] > 5 * MAXPASSATTEMPTS:
			print('max has been reached log in successful****')
			return True
		else:
			return False
	return False


'''
creates the starting state of the terminal session
touple consists of the current dir, files created, and list level
the files created list will contain the files that exist is each level
the last is the root
'''
def fakeTerminalSetup(chan):
	str = chan.get_transport().get_username() + '@honeypot:/$ '
	stateDirs = [[]]	#list of lists to contains items of levels
	chan.sendall(str)
	return [str,stateDirs,0,str]

'''
state = what is contained in the session
cmd is the current command
'''
def updateFakeTerminal(chan,state,cmd):
	cmd = cmd[:-1]
	split = cmd.split(' ')	#default is space
	print('SPLIT IS',split)

	if split[0] == 'ls':
		print('ls cmd')
		content = state[1][state[2]]	#gets the list at the curr level
		#if have more than zero things then show that else dont
		if len(content) > 0:
			toShow = ''
			for item in content:
				toShow += item + ' '
			toShow += '\n'
			chan.sendall(toShow)

	elif split[0] == 'mkdir':
		newDir = split[1]
		print('newdir is',newDir)
		state[1][state[2]].append(newDir)

	elif split[0] == 'cd':
		if len(split) > 1:
			goingTo = split[1]
			if goingTo in state[1][state[2]]:
				print('valid dir, going to',goingTo)
				updateLocation(state,goingTo)
		#going to root
		else:
			print('going to root')
			state[0] = state[3]
			state[2] = 0
	print('state is',state)
	chan.sendall(state[0])

'''
state[0] = curr dir
state[1] = list of files in a dir
state[2] = level which dir is current
state[3] = root dir
updates the curr dir
'''
def updateLocation(state,goingTo):
	split = state[0].split('$ ')
	print('split in update',split)
	state[0] = split[0] + goingTo + '/$ '
	state[1].append([])
	state[2] = state[2] + 1
	return

'''
server code that takes in the connections
'''
def serverCode(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#allows for reuse of address
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

	#bind the socket
	sock.bind(('127.0.0.1',port))
	sock.listen(MAXCONN)

	while 1:
		conn, cliAddr = sock.accept()
		print('got connection!!!')
		worker(conn,cliAddr)
	sock.close()

'''
worker function that does what is needed
to be done by all users that connect
does the communication between the channel
'''
def worker(conn,addr):
	t = paramiko.Transport(conn)
	t.add_server_key(hostKey)
	server = Server()
	try:
		t.start_server(server=server)
	except Exception as e:
		print('some error starting the server')
		exit(1)
	print('server created')
	chan = t.accept(20)

	if chan is not None:
		server.event.wait(10)
		if not server.event.is_set():
			print('no ask for a shell')
			exit(1)

		chan.sendall('\r\nWELCOME\r\n')
		state = fakeTerminalSetup(chan)
		while True:
			cmd = chan.recv(5120).decode()
			if not cmd:
				print('no got nothing leaving...')
				break
			print('GOT from client',cmd)
			updateFakeTerminal(chan,state,cmd)


if __name__ == '__main__':
	port = int(getArgs())

	setupUserDict()
	serverCode(port)
