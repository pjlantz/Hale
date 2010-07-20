################################################################################
#   (c) 2010, The Honeynet Project
#   Author: Patrik Lantz  patrik@pjlantz.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################

from utils import *
import moduleManager
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory

from xmpp import producerBot

@moduleManager.register("irc")
def setup_module(config):
    """
    Function to register modules, simply
    implement this to pass along the config
    to the module object and return it back
    """

    return IRC(config)

class IRC(moduleInterface.Module):
    """
    Implementation of a irc client to do irc based
    botnet monitoring
    """

    def __init__(self, config):
        """
        Constructor sets up configs and moduleCoordinator object
        """
        
        self.hash = hash
        self.config = config
         
    def run(self):
        """
        Start execution
        """
        
        factory = IRCClientFactory(self.config)
        host = self.config['botnet']
        port = int(self.config['port'])
        self.connector = reactor.connectTCP(host, port, factory)
        #socksify = socks5.ProxyClientCreator(reactor, factory)
        #self.connector = socksify.connectSocks5Proxy(host, port, "127.0.0.1", 1080, "HALE")
        
    def stop(self):
        """
        Stop execution
        """

        self.connector.disconnect()
        
                
    def getConfig(self):
        """
        Return specific configuration used by this module
        """
        
        return self.config
        
class IRCProtocol(Protocol):
    """
    Protocol taking care of connection, incoming
    data and outgoing
    """

    factory = None

    def connectionMade(self):
        """
        When connection is made
        """
        
        if self.factory.getConfig()['password'] != 'None':
            self.transport.write(self.factory.getConfig()['pass_grammar'] + ' ' + self.factory.getConfig()['password'] + '\r\n') # connect with pass
        self.transport.write(self.factory.getConfig()['nick_grammar'] + ' ' + self.factory.getConfig()['nick'] + '\r\n') # send NICK grammar
        self.transport.write(self.factory.getConfig()['user_grammar'] + ' ' + self.factory.getConfig()['username'] + ' ' +  
        self.factory.getConfig()['username'] + ' ' + self.factory.getConfig()['username'] + ' :' + 
        self.factory.getConfig()['realname'] + '\r\n') # sebd USER grammar

    def dataReceived(self, data):
        """
        Data is received
        """
        
        if data.find(self.factory.getConfig()['ping_grammar']) != -1: # ping
            self.transport.write(self.factory.getConfig()['pong_grammar'] + ' ' + data.split()[1] + '\r\n') # send pong
            if self.factory.getFirstPing():
				if self.factory.getConfig()['channel_pass'] != 'None': # joing with pass
				    self.transport.write(self.factory.getConfig()['join_grammar'] + ' ' + self.factory.getConfig()['channel'] + ' ' + 
				    self.factory.getConfig()['channel_pass'] + '\r\n')
				else:
				    self.transport.write(self.factory.getConfig()['join_grammar'] + ' ' + self.factory.getConfig()['channel'] + '\r\n') # join without pass
				self.factory.setFirstPing()
        elif data.find(self.factory.getConfig()['topic_grammar']) != -1: # topic
           pass
        elif data.find(self.factory.getConfig()['currenttopic_grammar']) != -1: # currenttopic
	        pass
        elif data.find(self.factory.getConfig()['privmsg_grammar']) != -1: # privmsg
            #moduleCoordinator.ModuleCoordinator().addEvent(md.LOG_EVENT, "Got irc messsage!") # todo with logging
            pass
        elif data.find(self.factory.getConfig()['notice_grammar']) != -1: # notice
            pass
        elif data.find(self.factory.getConfig()['mode_grammar']) != -1: # mode
            pass
        else: # log unrecognized commands, can also be MOTD and NAMES list
	        pass
	      
        #urlHandler.URLHandler(self.factory.getConfig(), data).start() #TODO without threads
        
class IRCClientFactory(ClientFactory):
    """
    Clientfactory for the IRCProtocol
    """

    protocol = IRCProtocol # tell base class what proto to build

    def __init__(self, config):
        """
        Constructor, sets first ping received flag
        and config to be used
        """
        
        self.config = config
        self.firstPing = True

    def getConfig(self):
        """
        Returns config 
        """
        
        return self.config
        
    def getFirstPing(self):
        """
        Returns get first ping flag
        """
        
        return self.getFirstPing
        
    def __call__(self):
        """
        Used by the socks5 module to return
        the protocol handled by this factory
        """
        
        p = self.protocol()
        p.factory = self
        return p
        
    def setFirstPing(self):
        """
        Set first ping flag to indicate
        that it has been received
        """
        
        self.firstPing = False
