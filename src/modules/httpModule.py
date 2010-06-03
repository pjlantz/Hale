# httpModule.py - example module
import moduleManager

def start():
    print "Running http bot"

@moduleManager.register("http")
def handle_config(config):
    """
    Handle configurations, then simply start
    the bot thread with this config.
    """
    print "Server: %s" % config["server"]
    print "Build_id: %s" % config["buildid"]
    start()