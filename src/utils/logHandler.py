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


# TODO LogHandler
import time
from twisted.internet import reactor, defer
from xmpp import producerBot

class LogHandler(object):

    def __init__(self):
        pass
        
    def handleLog(self, data, config):
        self.putToXMPP(data, config)
        self.putToDB(data, config)
            
    def putToDB(self, data, config):
        print "DB: " + data + " botnet:" + config['botnet']
        
    def putToXMPP(self, data, config):
        producerBot.ProducerBot().sendLog("botnet: " + config['botnet'])
        