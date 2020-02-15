# BeHappyBot
![Status: Complete](https://img.shields.io/badge/Status-Complete-green.svg)

A simple, expandable Python IRC bot.

Written to be simple, yet powerful, BeHappyBot can dynamically load modules written in Python. These modules have exposure to the full power of the IRC protocol, as well as of the bot itself, but use just enough abstraction to allow for quick and painless development.

##Installation##
To install BeHappyBot on a computer, use the following git commands. Doing so will clone the entire repository to the computer, then proceed to change you to the newly-created directory where everything downloaded.

    $ git clone https://github.com/Treebasher/BeHappyBot
    $ cd BeHappyBot

Assuming that you have Python installed, you can now run BeHappyBot with the following command.

    $ python BeHappyBot.py

##Updating##
Once BeHappyBot is installed, there are two methods to update it.

If you are simply a user of BeHappyBot, rather than a tinkerer or a developer, these will be enough for you. If you are doing more than just running BeHappyBot, however, you should look at the Wiki for more information.

###Method One###
Assuming that it has been installed and configured correctly, and assuming that it is connected to an IRC network, simply message it the following command (either in a channel that it is joined to, or in a private message).

    !updateyoself

This method actually gives all modules a chance to gracefully deinitialize themselves before the bot shuts down and updates. This may be important depending on the modules that are loaded at the time of update.

###Method Two###
If you prefer or necessitate a manual update of BeHappyBot, simple run the following command on the directory where you cloned the repository. It will update your repository with the latest code.

    $ git pull

You will then need to quit and restart BeHappyBot.

*Do note that this method may cause some loaded modules to lose data if they were expecting to be deinitialized before quitting.*
