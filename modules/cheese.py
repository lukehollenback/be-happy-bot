from globals import *

def init():
# Initialize the module when it is loaded
	print "[INFO] Let's get creamy!"
	
def bot_command(cmd, nick, host, client, args):
# This is called every time a bot command is found in a channel or private message
	global connection

	if cmd == "cheese":
		if client == connection["nickname"]:
			send("PRIVMSG", [nick, ":Where!!!!"])
		else:
			send("PRIVMSG", [client, ":Where!!!!"])

def irc_command(cmd, fromNick, fromHost, arguments):
# This is called for every single IRC command that is parsed
	print "[INFO] I don't know how to cream that"