from bot import *

## Initialize the module when it is loaded
def init(bot):
    print "> [INFO] Let's get creamy!"

## This is called every time a bot command is found in a channel or private message
def bot_command(bot, cmd, nick, host, client, args):
    if cmd == "cheese":
        if client == bot.connection["nickname"]:
            bot.send("PRIVMSG", [nick, ":Where!!!!"])
        else:
            bot.send("PRIVMSG", [client, ":Where!!!!"])

## This is called for every single IRC command that is parsed
def irc_command(bot, cmd, fromNick, fromHost, arguments):
    print "[INFO] I don't know how to cream that"

## De-initialize the module
def uninit(bot):
    print "[INFO] I guess we won't get creamy anymore"
