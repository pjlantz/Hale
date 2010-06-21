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

import moduleManager
import threading
import socket
from utils import *

@moduleManager.register("irc")
def handle_config(config, identifier):
    """
    Function to register modules, simply
    implement this to pass along the config
    and the module object to the threadManager
    """

    irc = IRC(config)
    threadManager.ThreadManager().add(irc, identifier)

class IRC(threading.Thread):
    """
    Implementation of a irc client to do irc based
    botnet monitoring
    """

    def __init__(self, config):
        """
        Constructor sets up configs etc.
        """
       
        self.continueThread = True
        self.config = config
        self.doJoin = False
        self.firstPing = True
        threading.Thread.__init__ (self)
   
    def __doConnect(self):
        """
        Setup socket and connect to irc server, then join channel
        """

        self.irc = socks.socksocket()
        self.irc.setproxy(socks.PROXY_TYPE_SOCKS5, 'pjlantz.com', 1020)
        
        self.irc.connect((self.config['network'], int(self.config['port'])))
        if self.config['password'] != 'None':
            self.irc.send(self.config['pass_grammar'] + ' ' + self.config['password'] + '\r\n')

        self.irc.send(self.config['nick_grammar'] + ' ' + self.config['nick'] + '\r\n')
        self.irc.send(self.config['user_grammar'] + ' ' + self.config['username'] + ' ' + 
        self.config['username'] + ' ' + self.config['username'] + ' :' + 
        self.config['realname'] + '\r\n')
            
    def __doJoin(self):
        """
        Join channel specified in the configuration
        """
        
        if self.config['channel_pass'] != 'None':
            self.irc.send(self.config['join_grammar'] + ' ' + self.config['channel'] + ' ' + 
            self.config['channel_pass'] + '\r\n')
        else:
            self.irc.send(self.config['join_grammar'] + ' ' + self.config['channel'] + '\r\n')
            
        self.doJoin = False      
            
    def doStop(self):
        """
        Stop this thread
        """
       
        self.continueThread = False
        self.irc.shutdown(socket.SHUT_RDWR)
       
    def run(self):
        """
        Make connection and define thread loop
        """
       
        self.__doConnect()
        while (self.continueThread):
            self.__handleProtocol()
        self.irc.close()
                   
    def __handleProtocol(self):
        """
        Handle incoming irc protocol and responses
        """
        
        if self.doJoin: # after registration
            self.__doJoin()
        
        data = self.irc.recv(1024)
      
        if data.find(self.config['ping_grammar']) != -1: # Ping
            self.irc.send(self.config['pong_grammar'] + ' ' + data.split()[1] + '\r\n') # Pong
            if self.firstPing:
                self.doJoin = True # registered and ready to join
                self.firstPing = False
            return
        if data.find(self.config['topic_grammar']) != -1: # Topic
            # Log topic info
            pass
        if data.find(self.config['currenttopic_grammar']) != -1: # Current topic
            # Log current topic info
            pass
        if data.find(self.config['privmsg_grammar']) != -1: # privmsg
            # Log privmsg
            pass
        if data.find(self.config['notice_grammar']) != -1: # notice
            # Log notice
            pass
                        
        urlHandler.URLHandler(self.config, data).start()
