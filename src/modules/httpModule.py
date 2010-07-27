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
from twisted.internet import reactor, protocol
from twisted.web.client import HTTPPageGetter

@moduleManager.register("http")
def setup_module(config, hash):
    """
    Function to register modules, simply
    implement this to pass along the config
    to the module object and return it back
    """

    return HTTP(config, hash)
    
class HTTP(moduleInterface.Module):
    """
    Implementation of a http client to do http based
    botnet monitoring by connecting to such botnets
    and receiving commands and instructions
    """
    
    def __init__(self, conf, hash):
        """
        Constructor sets up configs and task to do
        a looping call 
        """
        
        self.hash = hash
        self.config = conf
        self.cont = True
        
    def run(self):
        """
        Start execution
        """
        
        self.prox = proxySelector.ProxySelector()
        self.factory = HTTPClientFactory(self, self.hash, self.config)
        self.host = self.config['botnet']
        self.port = int(self.config['port'])
        self.proxyInfo = self.prox.getRandomProxy()
        if self.proxyInfo != None:
            self.proxyHost = self.proxyInfo['HOST']
            self.proxyPort = self.proxyInfo['PORT']
            self.proxyUser = self.proxyInfo['USER']
            self.proxyPass = self.proxyInfo['PASS']
        self.connect()
        
    def connect(self):
        """
        Scheduled function to execute which connects
        to botnet and receives instructions
        """
    
        if not self.cont:
            return
        
        if self.proxyInfo == None:
            self.connector = reactor.connectTCP(self.host, self.port, self.factory)
        else:
            socksify = socks5.ProxyClientCreator(reactor, self.factory)
            if len(self.proxyUser) == 0:
                self.connector = socksify.connectSocks5Proxy(self.host, self.port, self.proxyHost, self.proxyPort, "HALE")
            else:
                self.connector = socksify.connectSocks5Proxy(self.host, self.port, self.proxyHost, self.proxyPort, "HALE", self.proxyUser, self.proxyPass)        
            
    def startLoop(self):
        """
        Called by the factory to do a new reconnect
        """
        
        self.connect()
            
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
    """
    Protocol class fetching web page
    """

    def handleResponsePart(self, data):
        """
        Sends response to the factory
        """
        
        self.factory.handleResponse(data.strip())
        
class HTTPClientFactory(protocol.ClientFactory):
    """
    Clientfactory taking care of the http request
    """

    protocol = HTTPProtocol

    def __init__(self, module, hash, config):
        """
        Constructor
        """
        
        self.hash = hash
        self.config = config
        self.cookies = {}
        self.url = self.config['botnet']
        self.host = self.config['botnet']
        self.agent = self.config['useragent']
        self.path = self.config['path']
        self.method = self.config['method']
        self.req = urllib.urlencode({self.config['id_grammar']: self.config['id'], 
        self.config['build_id_grammar']: self.config['build_id']})
        if self.method == 'POST':
            self.headers = {"Host": self.host, "Content-Type": "application/x-www-form-urlencoded"}
            params = urllib.urlencode({self.config['id_grammar']: self.config['id'], 
            self.config['build_id_grammar']: self.config['build_id']})
            if self.config['use_base64encoding'] == "True":
                self.postdata = base64.b64encode(params)
            else:
                self.postdata = params
        if self.method == 'GET':
            self.headers = {"Host": self.host}
            if self.config['use_base64encoding'] == "True":
                idParameter = base64.b64encode(self.config['id'])
                buildIdParamter = base64.b64encode(self.config['build_id'])
                params = urllib.urlencode({self.config['id_grammar']: idParameter, self.config['build_id_grammar']: buildIdParamter})
            else:
               params = urllib.urlencode({self.config['id_grammar']: self.config['id'], 
               self.config['build_id_grammar']: self.config['build_id']}) 
            self.path = self.path + "?" + params
        self.wait = 0
        self.module = module
        
    def handleResponse(self, response):
        """
        Handles response by decoding it if specified to
        do so in the config file. Logs data and extract
        the new reconnect interval
        """
        
        if self.config['use_base64decoding'] == "True":
            try:
                response = base64.b64decode(response)
            except TypeError:
                # Could not decode data, maybe not base64 encoded, got response
                return
            
            # extract wait grammar for new reconnect interval
            moduleCoordinator.ModuleCoordinator().addEvent(moduleCoordinator.LOG_EVENT, response, self.hash, self.config)
            try:
                self.wait = int(response.split(self.config['wait_grammar'])[1].split(self.config['response_separator'])[1])
                reactor.callLater(self.wait * 60, self.module.startLoop)
            except IndexError:
                # Could not split out wait grammar, maybe base64 decoding is necessary, got response:
                return
                
    def __call__(self):
        """
        Used by the socks5 module to return
        the protocol handled by this factory
        """
        
        p = self.protocol()
        p.factory = self
        return p
    
    def gotStatus(self, version, status, message):
        pass
        
    def gotHeaders(self, headers):
        print headers
        
    def noPage(self, reason):
        pass
       
    def page(self, response):
        pass

        