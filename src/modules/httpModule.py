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

import threading
import base64
import httplib, urllib

import moduleManager
from utils import *

@moduleManager.register("http")
def setup_module(config):
    """
    Function to register modules, simply
    implement this to pass along the config
    to the module object and return it back
    """

    return HTTP(config)
    
class HTTP(moduleInterface.Module):
    """
    Implementation of a http client to do http based
    botnet monitoring by connecting to such botnets
    and receiving commands and instructions
    """
    
    def __init__(self, conf):
        """
        Constructor sets up configs, threadManager object
        and various booleans
        """
        
        self.continueThread = True
        self.tm = threadManager.ThreadManager()
        self.config = conf
        threading.Thread.__init__(self)
        
    def doStop(self):
        """
        Stop module execution
        """
        
        self.continueThread = False
        
    def run(self):
        """
        Thread method to execute on start()
        """
        
        #encoded = base64.b64encode('data to be encoded')
        #print "Encoded: " + encoded
        #data = base64.b64decode("MTA7MjAwMDsxMDswOzA7MzA7MTAwOzM7MjA7MTAwMDsyMDAwI3dhaXQjMTAjeENSMl8yNDNBRURCQQ==")
        #print "Decoded: " + data

        # POST method
        #print self.config['separator']
        conn = httplib.HTTPConnection("174.142.104.57", 3128) # fetch from a list with http proxies later
        params = urllib.urlencode({self.config['id_grammar']: self.config['id'], self.config['build_id_grammar']: self.config['build_id']})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn.request("POST", self.config['url'], params, headers)
        response = conn.getresponse()
        if response.status == 404:
            self.tm.putError(self.config['url'] + ": 404 Not Found", self)
        data = response.read()
        print data
        conn.close()


        