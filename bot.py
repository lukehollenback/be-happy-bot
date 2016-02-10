import os
import sys
import socket
from subprocess import Popen

##
## Add the path for modules
##

sys.path.insert(0, "./modules")

##
## BeHappyBot Class
##

class BeHappyBot:
    ##
    ## Initial configuration settings
    ## (Todo: Load all of this from a config file)
    ##

    def __init__(self):
        print "[INFO] BeHappyBot initialized"

    connection = {
        "network": "irc.slashnet.org",
        "port": 6667,
        "nickname": "BeHappyTest"
    }

    channels = [
        "#behappydev",
        "#spud"
    ]

    modules = {}

    debug = 0
    connected = False

    irc = None

    ##
    ## Various functions
    ##

    ## Send a message with the given command and arguments to the IRC server
    def send(self, command, arguments):
        message = command
        for argument in arguments:
            message = message + " " + argument

        self.irc.send(message + "\r\n")
        print "> [SENT] " + message

    ## Disconnect from the IRC server
    def disconnect(self):
        global irc, connected

        if self.irc is not None and self.connected is not None:
            self.send("QUIT", [])
            self.irc.close()
            self.irc = None
            self.connected = False
        else:
            print "[INFO] Cannot disconnect from server before being connected to it"

    ## Make sure that we are disconnected from the IRC server, then close the script
    def quit(self):
        self.disconnect()
        sys.exit(0)

    ## Make sure that we are disconnected from the IRC server, then open a new instance of the
    ## script, and then close our instance of the script
    def restart(self):
        self.disconnect()
        Popen(['python', 'behappy.py'])
        sys.exit(0)

    ##
    ## Functions for default commands
    ##

    ## Handle PRIVMSG commands
    def cmd_privmsg(self, nick, host, args):
        flag = False
        message = ""
        for arg in args:
            if flag is False and arg[0] == ":":  # The beginning of the actual message has been reached
                flag = True
                message += " " + arg[1:]

                # This will either be a channel or your nickname (depending on if it is a channel
                # message or a private message)
                client = args[(args.index(arg) - 1)]

                # Check if the message contains a bot command
                if arg[1] == "!":
                    subargs = args[(args.index(arg) + 1):]

                    # See if the bot command is in the list of default bot commands (not modules)
                    if arg[2:] in self.botCommands:
                        self.botCommands[arg[2:]](self, nick, host, client, subargs)

                    # Cycle through the modules and let them see if they can do anything with the
                    # command
                    for module in self.modules:
                        self.modules[module].bot_command(self, arg[2:], nick, host, client, subargs)
            elif flag is True:
                message += " " + arg

        print nick + ": " + message

    ## Handle the !random bot command
    def bot_random(self, nick, host, client, args):
        if client == self.connection["nickname"]:  # This command came in a PM
            self.send("PRIVMSG", [nick, ":Gahhhh"])
        else:  # This command was sent on a channel
            self.send("PRIVMSG", [client, ":Gahhhh"])

    ## Handle the !killyoself bot command
    def bot_quit(self, nick, host, client, args):
        self.quit()

    ## Handle the !jesusyoself bot command
    def bot_restart(self, nick, host, client, args):
        self.restart()

    ## Handle the !loadmodule [module] bot command
    def bot_loadmodule(self, nick, host, client, args):
        message = ""

        if len(args) == 1:
            filename = "modules/" + args[0] + ".py"
            if os.path.isfile(filename):
                module = __import__(args[0])
                self.modules[args[0]] = module

                self.modules[args[0]].init(self)

                message = "Module \"" + args[0] + "\" loaded"
            else:
                message = "Module \"" + args[0] + "\" does not exist"
        else:
            message = "No module specified"

        if client == self.connection["nickname"]:
            self.send("PRIVMSG", [nick, (":" + message)])
        else:
            self.send("PRIVMSG", [client, (":" + message)])

    def bot_unloadmodule(self, nick, host, client, args):
        message = ""

        if len(args) == 1:
            if args[0] in self.modules:
                self.modules[args[0]].uninit(self)
                self.modules.pop(args[0], None)

                message = "Module \"" + args[0] + "\" unloaded"
            else:
                message = "Module \"" + args[0] + "\" is not loaded"
        else:
            message = "No module specified"

        if client == self.connection["nickname"]:
            self.send("PRIVMSG", [nick, (":" + message)])
        else:
            self.send("PRIVMSG", [client, (":" + message)])

    ##
    ## Dictionary of default commands which can be handled
    ##

    ircCommands = {
        "PRIVMSG": cmd_privmsg
    }

    botCommands = {
        "random": bot_random,
        "killyoself": bot_quit,
        "jesusyoself": bot_restart,
        "loadmod": bot_loadmodule,
        "unloadmod": bot_unloadmodule
    }

    ##
    ## Basic runtime functions
    ##

    ## Connect to the IRC server and send initial identification information so that it accepts the
    ## connection
    def connect(self):
        ##
        ## Connect to the IRC server
        ##

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.connection["network"], self.connection["port"]))

        ##
        ## Tell the server who we want to be
        ##

        self.send("NICK", [self.connection["nickname"]])
        self.send("USER", [self.connection["nickname"],
                           self.connection["nickname"],
                           self.connection["nickname"],
                           ":Python IRC"]
                  )

    ## Run the endless loop which listens for messages from the server and does with them accordingly
    def run(self):
        while True:
            ##
            ## Split up the raw data that is received into messages (a.k.a. "data") because it
            ## potentially contains much more than a single message
            ##

            dataRaw = self.irc.recv(4096)
            dataSplit = dataRaw.split("\n")
            for data in dataSplit:
                if self.debug >= 2:
                    print data

                if len(data) > 0:
                    ##
                    ## Parse the data into a list structured like [sender, command, arguments], where,
                    ## especially sender, will need additional parsing and where arguments is, in
                    ## reality, a potentially infinite amount of additional list items
                    ##

                    dataStrip = data.rstrip('\r')  # Some servers don't obey the spec
                    message = dataStrip.split()

                    ##
                    ## Parse the data message
                    ## (Note: Handle commands that potentially are not headed with a sender first,
                    ## then break up all other types of messages and try to fire away their appropriate
                    ## function if possible)
                    ##

                    if message[0] == "PING":
                        self.send("PONG", [message[1]])

                        ##
                        ## If this is the first PING, confirm the connection is alive and proceed to
                        ## join the set channel(s)
                        ##

                        if not self.connected:
                            self.connected = True
                            print "> [INFO] Connection confirmed, attempting to join channels"
                            for channel in self.channels:
                                self.send("JOIN", [channel])
                    elif len(message) >= 2:
                        fromNick = message[0][1:]
                        fromHost = ""
                        fromHostPos = fromNick.find("!")
                        if fromHostPos != -1:
                            fromHost = fromNick[(fromHostPos + 1):]
                            fromNick = fromNick[0:fromHostPos]

                        arguments = message[2:]

                        if self.debug >= 1:
                            print "> [RCVD] Received command " + message[
                                1] + " from " + fromNick + " at host " + fromHost + "."

                        # See if the IRC command is in the list of default IRC commands (not modules)
                        if message[1] in self.ircCommands:
                            self.ircCommands[message[1]](self, fromNick, fromHost, arguments)

                        # Cycle through the modules and see if they can do anything with the command
                        for module in self.modules:
                            self.modules[module].irc_command(self, message[1], fromNick, fromHost, arguments)
                    elif self.debug >= 1:
                        print "> [RCVD] Received unknown command: "
                        print ">        " + data
