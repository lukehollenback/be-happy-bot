import bot


## Initialize the module when it is loaded
def init(robot):
    print "> [INFO] Let's get creamy!"


## This is called every time a bot command is found in a channel or private
## message
def bot_command(robot, cmd, nick, host, client, args):
    if cmd == "cheese":
        if client == robot.connection["nickname"]:
            robot.send("PRIVMSG", [nick, ":Where!!!!"])
        else:
            robot.send("PRIVMSG", [client, ":Where!!!!"])


## This is called for every single IRC command that is parsed
def irc_command(robot, cmd, nick, host, args):
    print "> [INFO] I don't know how to cream that"


## De-initialize the module
def uninit(robot):
    print "> [INFO] I guess we won't get creamy anymore"
