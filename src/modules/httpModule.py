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

import base64
import threading, time
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
        and thread execution flag
        """
        
        self.conn = None
        self.continueThread = True
        self.tm = threadManager.ThreadManager()
        self.config = conf
        threading.Thread.__init__(self)
        
    def doStop(self):
        """
        Stop module execution
        """
        
        self.continueThread = False
        self.conn.close()
        
    def run(self):
        """
        Connect through a http proxy to a http botnet and
        register yourself, fetch instructions and
        reconnect interval. Handles base64 encoding/decoding
        for requests/responses too.
        """

        while self.continueThread:
        
            self.conn = httplib.HTTPConnection("174.142.104.57", 3128) # fetch from a list with http proxies later
            params = urllib.urlencode({self.config['id_grammar']: self.config['id'], self.config['build_id_grammar']: self.config['build_id']})
            
            # POST method
            if self.config['method'] == "POST":
                # encode request
                if self.config['use_base64encoding'] == "True":
                    params = base64.b64encode(params)
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                self.conn.request("POST", self.config['url'], params, headers)
                
            # GET method
            if self.config['method'] == "GET":
                # encode parameters
                if self.config['use_base64encoding'] == "True":
                    idParameter = base64.b64encode(self.config['id'])
                    buildIdParamter = base64.b64encode(self.config['build_id'])
                    params = urllib.urlencode({self.config['id_grammar']: idParameter, self.config['build_id_grammar']: buildIdParamter})
                self.conn.request("GET", self.config['url'] + "?" + params)
            
            # get response
            response = self.conn.getresponse()
            if response.status != 200:
                self.tm.putError(self.config['url'] + ": " + str(response.status) + " status code", self)
                return
            data = response.read()
            self.conn.close()
            
            # decode response
            if self.config['use_base64decoding'] == "True":
                try:
                    data = base64.b64decode(data)
                except TypeError:
                    self.tm.putError("Could not decode data, maybe not base64 encoded, got response: " + data, self)
                    return                   
            
            # Log data
            print data
            urlHandler.URLHandler(self.config, data).start()
            
            # get wait grammar to know when to reconnect again
            try:
                wait = int(data.split(self.config['wait_grammar'])[1].split(self.config['response_separator'])[1])
            except IndexError:
                self.tm.putError("Could not split out wait grammar, maybe base64 decoding is necessary, got response: " + data, self)
                return
            time.sleep(wait)
        