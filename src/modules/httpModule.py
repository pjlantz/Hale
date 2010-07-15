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

import base64, urllib
import moduleManager
from utils import *

from twisted.internet import reactor, protocol, task
from twisted.web.client import HTTPPageGetter

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
        Constructor sets up configs
        """
        
        self.config = conf
        self.cont = True
        self.loop = task.LoopingCall(self.connect)
        
    def run(self):
        """
        Start execution
        """
        
        self.loop.start(1) # any value, reschedule later
        
    def connect(self):
        """
        Scheduled function to execute which connects
        to botnet and receives instructions
        """
    
        if self.cont:
	        factory = HTTPClientFactory(self.config)
	        host = self.config['botnet']
	        port = int(self.config['port'])
	        reactor.connectTCP(host, port, factory)
	        self.loop.stop()
	        self.loop.start(str(factory.getNewReconnect()), now=False)
        else:
            return
            
    def stop(self):
        """
        Stop execution
        """

        self.cont = False
        
                
    def getConfig(self):
        """
        Return specific configuration used by this module
        """
        
        return self.config
        
class HTTPProtocol(HTTPPageGetter):

    def handleResponsePart(self, data):
        self.factory.handleResponse(data.strip())
        
class HTTPClientFactory(protocol.ClientFactory):

    protocol = HTTPProtocol

    def __init__(self, config):
        self.config = config
        self.url = self.config['botnet']
        self.host = self.config['myhost']
        self.agent = self.config['useragent']
        self.path = self.config['path']
        self.headers = {"Host": self.host}
        self.method = self.config['method']
        self.req = urllib.urlencode({self.config['id_grammar']: self.config['id'], 
        self.config['build_id_grammar']: self.config['build_id']})
        if self.method == 'POST':
            params = urllib.urlencode({self.config['id_grammar']: self.config['id'], 
            self.config['build_id_grammar']: self.config['build_id']})
            if self.config['use_base64encoding'] == "True":
                self.postdata = base64.b64encode(params)
            else:
                self.postdata = params
        if self.method == 'GET':
            if self.config['use_base64encoding'] == "True":
                idParameter = base64.b64encode(self.config['id'])
                buildIdParamter = base64.b64encode(self.config['build_id'])
                params = urllib.urlencode({self.config['id_grammar']: idParameter, self.config['build_id_grammar']: buildIdParamter})
            else:
               params = urllib.urlencode({self.config['id_grammar']: self.config['id'], 
               self.config['build_id_grammar']: self.config['build_id']}) 
            self.path = self.path + "?" + params
        self.cookies = {}
        self.wait = 0
        
    def handleResponse(self, response):
        print response
        # decode response
        if self.config['use_base64decoding'] == "True":
            try:
                response = base64.b64decode(response)
            except TypeError:
                # Could not decode data, maybe not base64 encoded, got response
                return
            
            # extract wait grammar for new reconnect interval    
            try:
                self.wait = int(response.split(self.config['wait_grammar'])[1].split(self.config['response_separator'])[1])
            except IndexError:
                # Could not split out wait grammar, maybe base64 decoding is necessary, got response:
                return

    def getNewReconnect(self):
        """
        Return new reconnect interval
        """
        
        return self.wait * 60
    
    def gotStatus(self, version, status, message):
        pass
        
    def gotHeaders(self, headers):
        pass
        
    def noPage(self, reason):
        pass
       
    def page(self, response):
        pass

        