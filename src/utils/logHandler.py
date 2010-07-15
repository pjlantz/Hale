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

class Singleton(type):
    """
    Singleton pattern used to only create one 
    LogHandler instance
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

class LogHandler(object):

    __metaclass__ = Singleton
        
    def handleLog(self, data):
        d = self.putToXMPP(data)
        if d != None:
            d.addCallback(self.putToDB)
            
    def putToDB(self, data):
        time.sleep(2)
        print "DB: " + data
        
    def putToXMPP(self, data):
        d = defer.Deferred()
        print "XMPP: " + data
        reactor.callLater(0, d.callback, data)
        return d 
        
        