# ircModule.py - example module
import moduleManager
        
def start():
    print "Running irc bot"

@moduleManager.register("irc")
def handle_config(config):
    """
    Handle configurations, then simply start
    the bot thread with this config.
    """
    print "Nick: %s" % config["nick"]
    print "Channel: %s" % config["channel"]
    start()