#!/usr/bin/python

import sys
import bot

# Make sure that this file is being executed rather than imported
if __name__ == "__main__":
    robot = bot.BeHappyBot()

    if len(sys.argv) == 2 and sys.argv[1] == "--makeconf": # Generate a config file
        print "In order to create a configuration file for BeHappyBot, you will be asked some questions."
        print "Please be aware that this will overwrite any existing configuration file that you may have created."

        res = raw_input("Would you like to proceed? (y/n)\n")
        if res == "n" or res == "no":
            quit()

        res = raw_input("What server would you like BeHappyBot to connect to? (e.g. irc.slashnet.org)\n")
        robot.connection["network"] = str(res) if res != "" else "irc.slashnet.org"
        res = raw_input("What port should it connect to " + res + " on? (e.g. 6667)\n")
        robot.connection["port"] = int(res) if res != "" else 6667
        res = raw_input("What would you like BeHappyBot's nickname to be?\n")
        robot.connection["nickname"] = str(res) if res != "" else "BeHappyBot"
        res = raw_input("Enter a space-delimited list of the channels " + res + " should join upon connection... (e.g. webdev #cheese #california)\n")
        robot.channels = res.split()

        robot.save_configuration()

        print "A configuration file has been generated. Re-run BeHappyBot like normal to use it."
    else: # Run the actual bot
        robot.load_configuration()
        robot.connect()
        robot.run()
