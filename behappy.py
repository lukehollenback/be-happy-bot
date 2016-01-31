import sys, socket

##
## Initial configuration settings
##

network = "irc.slashnet.org"
port = 6667
channel = "#behappydev"
nickname = "BeHappy"

debug = 0
connected = False

##
## Connect to the IRC server
##

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((network, port))

##
## Various commands
##

def send(cmd, args):
# Send a message with the given command and arguments to the IRC server
	msg = cmd
	for arg in args:
		msg = msg + " " + arg
	
	irc.send(msg + "\r\n")
	print "> [SENT] " + msg
	
##
## Dictionary of commands which can be handled
## (Note: The functions held in this dictionary accept a list of arguments as a paramater; ircCommands accept the arguments of the received messaged, and botCommands except the arguments of the bot command (which are the latter part of a PRIVMSG containing a bot command))
##

def cmd_privmsg(nick, host, args):
# Handle PRIVMSG commands
	flag = False
	message = ""
	for arg in args:
		if flag == False and arg[0] == ":": # The beginning of the actual message has been reached
			flag = True
			message += " " + arg[1:]
			
			if arg[1] == "!": # This message contains a bot command
				if arg[2:] in botCommands:
					subargs = args[(args.position(arg) + 1):]
					botCommands[arg[2:]](nick, host, subargs)
		elif flag == True:
			message += " " + arg
	
	print nick + ": " + message

def bot_random(nick, host, args):
	send("PRIVMSG", [nick, ":Gahhhh"])

def bot_quit(nick, host, args):
	send("QUIT", [])
	irc.close();
	sys.exit(0);

ircCommands = {
	"PRIVMSG" : cmd_privmsg
	}
	
botCommands = {
	"random" : bot_random,
	"killyoself" : bot_quit
}
	
##
## Tell the server who we want to be
##

send("NICK", [nickname])
send("USER", [nickname, nickname, nickname, ":Python IRC"])

##
## The endless loop which listens for messages from the server and does with them accordingly
##

while True:
	##
	## Split up the raw data that is received into messages (a.k.a. "data") because it potentially contains much more than a single message
	##
	
	dataRaw = irc.recv(4096)
	dataSplit = dataRaw.split("\n")
	for data in dataSplit:
		if debug >= 2:
			print data
			
		if len(data) > 0:
			##
			## Parse the data into a list structured like [sender, command, arguments], where, especially sender, will need additional parsing and where arguments is, in reality, a potentially infinite amount of additional list items
			##
			
			dataStrip = data.rstrip('\r') # Some servers don't obey the spec
			message = dataStrip.split()
			
			##
			## Parse the data message
			## (Note: Handle commands that potentially are not headed with a sender first, then break up all other types of messages and try to fire away their appropriate function if possible)
			##
			
			if message[0] == "PING":
				send("PONG", [message[1]])
				
				##
				## If this is the first PING, confirm the connection is alive and proceed to join the set channel(s)
				##
				
				if not connected:
					connected = True
					print "> [INFO] Connection confirmed, attempting to join channels"
					send("JOIN", [channel])
			elif len(message) >= 2:
				fromNick = message[0][1:]
				fromHost = ""
				fromHostPos = fromNick.find("!")
				if fromHostPos != -1:
					fromHost = fromNick[(fromHostPos + 1):]
					fromNick = fromNick[0:fromHostPos]
		
				arguments = message[2:]
		
				if debug >= 1:
					print "> [RCVD] Recieved command " + message[1] + " from " + fromNick + " at host " + fromHost + "."
		
				if message[1] in ircCommands:
					ircCommands[message[1]](fromNick, fromHost, arguments)
			elif debug >= 1:
				print "> [RCVD] Recieved unknown command: "
				print ">        " + data