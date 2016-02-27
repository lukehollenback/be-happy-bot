import os
import sys
import socket
from subprocess import Popen, check_output


##
## Add the path for modules
##

sys.path.insert(0, "./modules")


##
## BeHappyBot Class
##

class BeHappyBot:

    connection = {}
    channels = []
    modules = {}
    irc = None

    debug = 0
    connected = False

    ##
    ## Initial configuration settings
    ##

    def __init__(self):
        if os.path.isfile("behappy.conf"):
            self.load_configuration()
            print "> [INFO] Existing configuration file found and loaded"
        else:
            print "> [INFO] No configuration file found (try running BeHappyBot with --makeconf)"

        print "> [INFO] BeHappyBot initialized"

    ##
    ## Various functions
    ##

    ## Load the configuration from behappy.conf
    def load_configuration(self):
        filename = "behappy.conf"
        if os.path.isfile(filename):
            conf_file = open(filename, "r")

            data = ""
            buff = conf_file.read()
            while buff != "":
                data += buff
                buff = conf_file.read()

            data_split = data.split("\n")
            for line in data_split:
                line_split = line.split()

                if len(line_split) >= 3:
                    if line_split[0] == "network":
                        self.connection["network"] = line_split[2]
                    elif line_split[0] == "port":
                        self.connection["port"] = int(line_split[2])
                    elif line_split[0] == "nickname":
                        self.connection["nickname"] = line_split[2]
                    elif line_split[0] == "channels":
                        for channel in line_split[2:]:
                            if channel not in self.channels:
                                # Note: I'm not sure why, but each channel will be added to the list twice without this
                                # check in place
                                self.channels.append(channel)
                    elif line_split[0] == "modules":
                        for module in line_split[2:]:
                            if module not in self.modules:
                                # Note: I'm not sure why, but each module will be loaded twice without this check in place
                                self.load_module(module)

            conf_file.close()
        else:
            print "> [INFO] No configuration file found; Run with --makeconf, or manually create a behappy.conf file"
            quit()

    ## Save the current configuration
    def save_configuration(self):
        conf_file = open("behappy.conf", "w")

        # Write basic settings
        conf_file.write("network = " + self.connection["network"] + "\n")
        conf_file.write("port = " + str(self.connection["port"]) + "\n")
        conf_file.write("nickname = " + self.connection["nickname"] + "\n")

        # Write currently joined channels
        joined_channels = ""
        for channel in self.channels:
            # If there is more that one channel, delimit them with spaces
            if joined_channels != "":
                joined_channels += " "

            joined_channels += channel
        conf_file.write("channels = " + joined_channels + "\n")

        # Write currently loaded modules
        loaded_modules = ""
        for module in self.modules:
            # If there is more than one module, delimit them with spaces
            if loaded_modules != "":
                loaded_modules += " "

            loaded_modules += module
        conf_file.write("modules = " + loaded_modules)

        conf_file.close()

    ## Send a message with the given command and arguments to the IRC server
    def send(self, command, arguments):
        message = command
        for argument in arguments:
            message = message + " " + argument

        self.irc.send(message + "\r\n")
        print "> [SENT] " + message

    ## Disconnect from the IRC server
    def disconnect(self):
        if self.irc is not None and self.connected is not None:
            self.send("QUIT", [])
            self.irc.close()
            self.irc = None
            self.connected = False
        else:
            print "[INFO] Cannot disconnect from server before being connected to it"

    ## Make sure that we are disconnected from the IRC server, then close the script
    def quit(self):
        # Save the current configuration
        self.save_configuration()

        # Allow any loaded modules to unload
        for module in self.modules:
            self.modules[module].uninit(self)

        # Disconnect and close
        self.disconnect()
        quit()

    ## Make sure that we are disconnected from the IRC server, then open a new instance of the
    ## script, and then close our instance of the script
    def restart(self):
        # Save the current configuration
        self.save_configuration()

        # Allow any loaded modules to unload
        for module in self.modules:
            self.modules[module].uninit(self)

        # Disconnect, open again, then close
        self.disconnect()
        Popen(['python', 'behappy.py'])
        quit()

    ## Attempt to load a module
    ## PARAM name: The name of the module to load (e.g. "cheese" for the "cheese.py" module file)
    ## RETURN: True when successful, False when module does not exist
    def load_module(self, name):
        filename = "modules/" + name + ".py"
        if os.path.isfile(filename):
            module = __import__(name)
            self.modules[name] = module

            self.modules[name].init(self)

            return True
        else:
            return False

    ## Attempt to unload a loaded module
    ## PARAM name: The name of the loaded module to unload
    ## RETURN: True when a loaded module was found and unloaded, False when the specified module is not found to be
    ##         loaded
    def unload_module(self, name):
        if name in self.modules:
            self.modules[name].uninit(self)
            self.modules.pop(name, None)

            return True
        else:
            return False

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

                # Get the client that is supposed to receive the PRIVMSG
                # (Note: This will either be a channel or your nickname depending on if it is a channel
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

    ## Handle the !updateyoself bot command
    def bot_update(self, nick, host, client, args):
        # Pull from git
        output = check_output(['git', 'pull'])
        output_split = output.split('\n')
        for line in output_split:
            line_strip = line.rstrip('\r').lstrip('\r')  # We should clean up unknown output
            if line_strip != "":
                print "> [UPDT] " + line_strip

        # Restart the bot
        self.restart()

    ## Handle the !loadmodule [module] bot command
    def bot_loadmodule(self, nick, host, client, args):
        message = ""

        if len(args) == 1:
            if self.load_module(args[0]):
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
            if self.unload_module(args[0]):
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
        "updateyoself": bot_update,
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
                           ":BeHappy IRC Bot"]
                  )

    ## Run the endless loop which listens for messages from the server and does with them accordingly
    def run(self):
        while True:
            ##
            ## Split up the raw data that is received into messages (a.k.a. "data") because it
            ## potentially contains much more than a single message
            ##

            data_raw = self.irc.recv(4096)
            data_split = data_raw.split("\n")
            for data in data_split:
                if self.debug >= 2:
                    print data

                if len(data) > 0:
                    ##
                    ## Parse the data into a list structured like [sender, command, arguments], where,
                    ## especially sender, will need additional parsing and where arguments is, in
                    ## reality, a potentially infinite amount of additional list items
                    ##

                    data_strip = data.rstrip('\r')  # Some servers don't obey the spec
                    message = data_strip.split()

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
                        from_nick = message[0][1:]
                        from_host = ""
                        from_host_pos = from_nick.find("!")
                        if from_host_pos != -1:
                            from_host = from_nick[(from_host_pos + 1):]
                            from_nick = from_nick[0:from_host_pos]

                        arguments = message[2:]

                        if self.debug >= 1:
                            print "> [RCVD] Received command " + message[
                                1] + " from " + from_nick + " at host " + from_host + "."

                        # See if the IRC command is in the list of default IRC commands (not modules)
                        if message[1] in self.ircCommands:
                            self.ircCommands[message[1]](self, from_nick, from_host, arguments)

                        # Cycle through the modules and see if they can do anything with the command
                        for module in self.modules:
                            self.modules[module].irc_command(self, message[1], from_nick, from_host, arguments)
                    elif self.debug >= 1:
                        print "> [RCVD] Received unknown command: "
                        print ">        " + data
