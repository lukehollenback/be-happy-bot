#!/usr/bin/python

import sys
import bot

# Make sure that this file is being executed rather than imported
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--makeconf":  # Generate a config file
        print "Make config!"
    else:  # Run the actual bot
        rob = bot.BeHappyBot()

        rob.connect()
        rob.run()
