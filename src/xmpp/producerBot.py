################################################################################
# (c) 2010, The Honeynet Project
# Author: Patrik Lantz patrik@pjlantz.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
################################################################################

import sleekxmpp, random, time
from threading import Lock
import threading, hashlib
from conf import configHandler

class synchronized(object):
    """
    Class enapsulating a lock and a function
    allowing it to be used as a synchronizing
    decorator making the wrapped function
    thread-safe
    """
    
    def __init__(self, *args):
        self.lock = Lock()
        
    def __call__(self, f):
        def lockedfunc(*args, **kwargs):
            try:
                self.lock.acquire()
                try:
                    return f(*args, **kwargs)
                except Exception, e:
                    raise
            finally:
                self.lock.release()

        return lockedfunc

class Singleton(type):
    """
    Singleton pattern used to only create one
    ProducerBot instance
    """
    
    def __init__(cls, name, bases, dict):
        """
        Constructor
        """
        
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None
 
    def __call__(cls, *args, **kw):
        """
        Return instance
        """
        
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
 
        return cls.instance

class StartTrack(threading.Thread):

    def __init__(self, producer):
    
        self.eventlist = list()
        self.producer = producer
        self.nbrOfBotnets = 0
        threading.Thread.__init__(self)
        
    def run(self):
    
        while True:
            self.nbrOfBotnets = len(self.producer.getMonitoredBotnets())
            time.sleep(self.nbrOfBotnets * 10)
            if len(self.eventlist) > 0:
                config = self.eventlist.pop()
                from utils import moduleCoordinator
                eventType = moduleCoordinator.START_EVENT
                moduleCoordinator.ModuleCoordinator().addEvent(eventType, config)
            
    def addMessage(self, data):
    
        self.eventlist.append(data)
       
class ProducerBot(threading.Thread):
    """
    Producer put logs to a group room on a
    XMPP server
    """
    
    __metaclass__ = Singleton
    
    def __init__(self, xmppConf):
        """
        Constructor, set up event handlers and register
        plugins
        """
        
        self.running = False
        self.currentHash = 0
        self.monitoredBotnets = []
        self.foundTrack = False
        self.startTrackThread = StartTrack(self)
        self.password = xmppConf.get("xmpp", "password")
        self.server = xmppConf.get("xmpp", "server")
        self.jid = xmppConf.get("xmpp", "jid");
        self.sharechannel = xmppConf.get("xmpp", "datashare_channel") + "@conference." + self.server
        self.coordchannel = xmppConf.get("xmpp", "coordination_channel") + "@conference." + self.server
        
        self.port = xmppConf.get("xmpp", "port")
        self.xmpp = sleekxmpp.ClientXMPP(self.jid, self.password)
        self.xmpp.registerPlugin("xep_0045")
        self.xmpp.add_event_handler("session_start", self.handleXMPPConnected)
        self.xmpp.add_event_handler("disconnected", self.handleXMPPDisconnected)
        self.xmpp.add_event_handler("groupchat_message", self.handleIncomingGroupChatMessage)
        threading.Thread.__init__(self)
        
    def disconnectBot(self, reconnect=False):
        """
        Close connection to XMPP server
        """
        
        if self.running:
            self.xmpp.disconnect(reconnect)
        
    def run(self):
        """
        Connect to XMPP server and start xmpp
        process
        """

        self.xmpp.connect((self.server, int(self.port)))
        self.xmpp.process()
        
    def handleXMPPDisconnected(self, event):
        """
        Handle disconnected state
        """
    
        print ""

    def handleXMPPConnected(self, event):
        """
        On sucessful connection join specified
        group room
        """

        self.startTrackThread.start()
        self.running = True
        self.xmpp.sendPresence()
        muc = self.xmpp.plugin["xep_0045"]
        nick = self.jid.split('@')[0]
        muc.joinMUC(self.sharechannel, nick)
        muc.joinMUC(self.coordchannel, nick)
                    
    @synchronized()
    def sendTrackReq(self, botnet):
        """
        Send a trackReq to let other sensors know
        that its going to monitor a specific botnet.
        Returns False if the request does not receive a
        an ack on this request, meaning no one is monitoring
        the botnet. Otherwise True if someone is monitoring.
        """
        
        msg = 'trackReq ' + botnet
        self.xmpp.sendMessage(self.coordchannel, msg, None, "groupchat")
        time.sleep(2)
        self.currentHash = botnet
        if self.foundTrack:
            self.foundTrack = False
            return True
        self.monitoredBotnets.append(botnet)
        return False
        
    def removeBotnet(self, botnet):
        """
        Remove a botnet from the list of
        monited ones
        """
        
        self.monitoredBotnets.remove(botnet)
        
    def getMonitoredBotnets(self):
        """
        Return the list of monitored botnets
        """
        
        return self.monitoredBotnets
        
    def handleIncomingGroupChatMessage(self, message):
        """
        Handles groupchat messages from the coordination
        channel
        """
        
        channel = str(message['from'])
        coordchan = self.coordchannel.split('@')[0]
        if channel.split('@')[0] == coordchan:
            body = message['body'].split(' ')
            if len(body) == 2 and body[0] == 'trackReq':
                botnetStr = body[1]
                
                if botnetStr in self.monitoredBotnets:
                    msg = 'trackAck ' + botnetStr
                    self.xmpp.sendMessage(self.coordchannel, msg, None, "groupchat")
                    
            if len(body) == 2 and body[0] == 'trackAck':
                botnetStr = body[1]
                if self.currentHash == botnetStr:
                    self.foundTrack = True
            
            if body[0] == 'startTrack':
                config = ' '.join(body).split('startTrack')[1]
                self.startTrackThread.addMessage(config)
    
    def sendLog(self, msg):
        """
        Send logs to the data sharing channel
        """
        
        self.xmpp.sendMessage(self.sharechannel, msg, None, "groupchat")
        