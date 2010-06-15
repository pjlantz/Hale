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
    and start the module thread
    """

    irc = IRC(config)
    threadManager.ThreadManager().add(irc, identifier)

class IRC(threading.Thread):

   def __init__(self, config):
       """
       Constructor sets up configs etc.
       """
       
       self.continueThread = True
       self.config = config
       threading.Thread.__init__ (self)
   
   def doConnect(self):
       """
       Setup socket and connect to irc server, then join channel
       """

       self.irc = socks.socksocket()
       self.irc.setproxy(socks.PROXY_TYPE_SOCKS5, "pjlantz.com", 1020)
       self.irc.connect((self.config['network'], int(self.config['port'])))
       self.irc.send(self.config['nick_grammar'] + ' ' + self.config['nick'] + '\r\n')
       self.irc.send(self.config['user_grammar'] + ' spybot spybot spybot :Python IRC\r\n')
       self.irc.send(self.config['join_grammar'] + ' ' + self.config['channel'] + ' ' + self.config['channel_pass'] + '\r\n')
       
   def doStop(self):
       """
       Stop this thread
       """
       
       self.continueThread = False
       
   def run(self):
       """
       Handles incoming irc protocol
       """
       
       self.doConnect()
       while (self.continueThread):
           data = self.irc.recv(4096)
           if data.find('PING') != -1:
              self.irc.send ('PONG ' + data.split() [1] + '\r\n')
