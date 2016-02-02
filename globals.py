import os
import sys
import socket
from subprocess import Popen

##
## Add the path for modules
##

sys.path.insert(0, "./modules")

##
## Initial configuration settings
## (Todo: Load all of this from a config file)
##

connection = {
	"network" : "irc.slashnet.org",
	"port" : 6667,
	"nickname" : "BeHappy"
	}
	
channels = [
	"#behappydev",
	"#spud"
	]
	
modules = { }

debug = 0
connected = False

irc = None

##
## Various functions
##

def send(command, arguments):
# Send a message with the given command and arguments to the IRC server
	global irc

	message = command
	for argument in arguments:
		message = message + " " + argument
	
	irc.send(message + "\r\n")
	print "> [SENT] " + message
	
def disconnect():
# Disconnect from the IRC server
	global irc, connected

	if irc != None and connected != None:
		send("QUIT", [])
		irc.close();
		irc = None
		connected = False
	else:
		print "[INFO] Cannot disconnect from server before being connected to it"
	
def quit():
# Make sure that we are disconnected from the IRC server, then close the script
	disconnect()
	sys.exit(0)
	
def restart():
# Make sure that we are disconnected from the IRC server, then open a new instance of the script, and then close our instance of the script
	disconnect()
	Popen(['python', 'behappy.py'])
	sys.exit(0)
	
##
## Functions for default commands
##

def cmd_privmsg(nick, host, args):
# Handle PRIVMSG commands
	flag = False
	message = ""
	for arg in args:
		if flag == False and arg[0] == ":": # The beginning of the actual message has been reached
			flag = True
			message += " " + arg[1:]
			
			client = args[(args.index(arg) - 1)] # This will either be a channel or your nickname (depending on if it is a channel message or a private message)
			
			if arg[1] == "!": # This message contains a bot command
				subargs = args[(args.index(arg) + 1):]
				
				if arg[2:] in botCommands: # See if the bot command is in the list of default bot commands (not modules)
					botCommands[arg[2:]](nick, host, client, subargs)
				
				for module in modules: # Cycle through the modules and let them see if they can do anything with the command
					modules[module].bot_command(arg[2:], nick, host, client, subargs)
		elif flag == True:
			message += " " + arg
	
	print nick + ": " + message

def bot_random(nick, host, client, args):
# Handle the !random bot command
	global connection
	
	if client == connection["nickname"]: # This command came in a PM
		send("PRIVMSG", [nick, ":Gahhhh"])
	else: # This command was sent on a channel
		send("PRIVMSG", [client, ":Gahhhh"])

def bot_quit(nick, host, client, args):
# Handle the !killyoself bot command
	quit()
	
def bot_restart(nick, host, client, args):
# Handle the !jesusyoself bot command
	restart()
	
def bot_loadmodule(nick, host, client, args):
# Handle the !loadmodule [module] bot command
	global modules, connection
	message = ""
	
	if len(args) == 1:
		filename = "modules/" + args[0] + ".py"
		if os.path.isfile(filename):
			module = __import__(args[0])
			modules[args[0]] = module
			
			modules[args[0]].init()
			
			message = "Module \"" + args[0] + "\" loaded"
		else:
			message = "Module \"" + args[0] + "\" does not exist"
	else:
		message = "No module specified"
	
	if client == connection["nickname"]:
		send("PRIVMSG", [nick, (":" + message)])
	else:
		send("PRIVMSG", [client, (":" + message)])

def bot_unloadmodule(nick, host, client, args):
	global modules, connection
	message = ""
	
	if len(args) == 1:
		if args[0] in modules:
			modules[args[0]].uninit()
			p = modules.pop(args[0], None)
			if p != None:
				p = None
			
			message = "Module \"" + args[0] + "\" unloaded"
		else:
			message = "Module \"" + args[0] + "\" is not loaded"
	else:
		message = "No module specified"
		
	if client == connection["nickname"]:
		send("PRIVMSG", [nick, (":" + message)])
	else:
		send("PRIVMSG", [client, (":" + message)])
	
##
## Dictionary of default commands which can be handled
##

ircCommands = {
	"PRIVMSG" : cmd_privmsg
	}
	
botCommands = {
	"random" : bot_random,
	"killyoself" : bot_quit,
	"jesusyoself" : bot_restart,
	"loadmod" : bot_loadmodule,
	"unloadmod": bot_unloadmodule
}

##
## Basic runtime functions
##

def connect():
# Connect to the IRC server and send initial identification information so that it accepts the connection
	global irc, connection

	##
	## Connect to the IRC server
	##

	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	irc.connect((connection["network"], connection["port"]))
	
	##
	## Tell the server who we want to be
	##

	send("NICK", [connection["nickname"]])
	send("USER", [connection["nickname"], connection["nickname"], connection["nickname"], ":Python IRC"])

def run():
# Run the endless loop which listens for messages from the server and does with them accordingly
	global irc, connected, debug, connection, channels, modules

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
						for channel in channels:
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
		
					if message[1] in ircCommands: # See if the IRC command is in the list of default IRC commands (not modules)
						ircCommands[message[1]](fromNick, fromHost, arguments)
						
					for module in modules: # Cycle through the modules and see if they can do anything with the command
						modules[module].irc_command(message[1], fromNick, fromHost, arguments)
				elif debug >= 1:
					print "> [RCVD] Recieved unknown command: "
					print ">        " + data