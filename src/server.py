#############################################################################
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

import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer

from conf import configHandler
from modules import moduleManager
from utils import moduleCoordinator
from xmpp import producerBot
from ConfigParser import *

import socket, os, base64
import sys, signal, threading, time
from OpenSSL import SSL

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

os.environ["DJANGO_SETTINGS_MODULE"] = "webdb.settings"
        
class ModuleDirChangeThread(threading.Thread):
    """
    This thread calls the function 'load_modules'
    in moduleManager periodically to check for 
    newly registered modules and recently removed
    """

    def __init__(self):
        """
        Constructor, sets continue flag
        """
        
        self.continueThis = True
        threading.Thread.__init__ (self)

    def run(self):
        """
        Handles the call to 'load_modules'
        """
        
        while self.continueThis:
            moduleManager.load_modules()
            time.sleep(1)
            
    def stop(self):
        """
        Mark the continue flag to stop thread
        """
        
        self.continueThis = False

class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def __init__(self, server_address, HandlerClass, logRequests=False):
        """
        Secure XML-RPC server.
        It it very similar to SimpleXMLRPCServer but it uses HTTPS for transporting XML data.
        """

        self.logRequests = logRequests
        haleConf = configHandler.ConfigHandler().loadHaleConf()
        keyfile = os.getcwd() + '/certs/' + haleConf.get("server", "key")
        certfile = os.getcwd() + '/certs/' + haleConf.get("server", "cert")
        if os.name == "nt":
            keyfile = keyfile.replace("/", "\\")
            certfile = certfile.replace("/", "\\")

        SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
        SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        
        try:
            ctx.use_privatekey_file(keyfile)
        except SSL.Error:
            print "No such key file: " + keyfile
            sys.exit(1)
        try:
            ctx.use_certificate_file(certfile)
        except SSL.Error:
            print "No such cert file: " + certfile
            sys.exit(1)

        self.socket = SSL.Connection(ctx, socket.socket(self.address_family, self.socket_type))
        self.server_bind()
        self.server_activate()

class SecureXMLRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """
    Secure XML-RPC request handler class.
    It it very similar to SimpleXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
    """

    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)
        
    def do_POST(self):
        """
        Handles the HTTPS POST request.
        It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
        """

        if not self.authenticate_client():
            return

        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(data, getattr(self, '_dispatch', None))
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown() # Modified here!

    def authenticate_client(self):
        if self.headers.has_key('Authorization'):
            
            (enctype, encstr) =  self.headers.get('Authorization').split()
            (user, passwd) = base64.standard_b64decode(encstr).split(':')
            try:
                u = User.objects.get(username__exact=user)
            except User.DoesNotExist:
                return False
            if u.check_password(passwd) and u.is_staff == True:
                return True
            return False
    
def main(HandlerClass = SecureXMLRpcRequestHandler,ServerClass = SecureXMLRPCServer):
    """
    XML-RPC over https server
    """

    class xmlrpc_registers:
        """
        Instance with methods to be called
        """

        def __init__(self):
            """
            Constructor to set up objects to be used
            """

            import string
            self.python_string = string
            moduleManager.handle_modules_onstart()
            moduleCoordinator.ModuleCoordinator().start()
            self.haleConf = configHandler.ConfigHandler().loadHaleConf()
            if self.haleConf.get("xmpp", "use") == 'True':
                producerBot.ProducerBot(self.haleConf).run()
            self.moduleDirChange = ModuleDirChangeThread()
            self.moduleDirChange.start()
            self.config = configHandler.ConfigHandler()
            self.modlist = []

        def auth(self, arg):
            """
            Used for authentication
            """

            return ""

        def lsmod(self, arg):
            """
            Return all installed modules
            """

            lsStr = "\nInstalled modules\n=================\n"
            self.modlist = moduleManager.get_modules()
            for mod in self.modlist:
                lsStr += mod + "\n"
            return lsStr

        def execmod(self, arg):
            """
            Start a module
            """

            args = arg.split(' ')
            if len(args) < 2:
                return "Usage: exec modulename identifier"
            arg3 = configHandler.ConfigHandler().getCurrentHash()
            errorStr = moduleManager.execute(args[0], args[1], arg3)
            if len(errorStr) > 0:
                return errorStr

        def stopmod(self, arg):
            """
            Stop a specific module
            """

            errorStr = moduleCoordinator.ModuleCoordinator().stop(arg)
            if len(errorStr) > 0:
                return errorStr

        def lsexec(self, arg):
            """
            Return modules currently running
            """

            idlist = moduleCoordinator.ModuleCoordinator().getAll()
            if len(idlist) == 0:
                return "No modules running"
            else:
                listStr = "\nModule ID\n=========\n"
                for ident in idlist:
                    listStr += ident + "\n"
                return listStr

        def execinfo(self, arg):
            """
            Return info about modules running
            """

            info = moduleCoordinator.ModuleCoordinator().getInfo(arg)
            if len(info) == 0:
                return "No such id running"
            infoStr = "\nModule ID\tHash\n=========\t=================\n"
            infoStr += arg + "\t" + info + "\n"
            return infoStr

        def lsconf(self, arg):
            """
            List existing configurations
            """

            return self.config.listConf()

        def reloadmod(self, arg):
            """
            Reload a module file
            """

            errorStr = moduleManager.reload_module(arg)
            if len(errorStr) > 0:
                return errorStr

        def useconf(self, arg):
            """
            Use specific configuration
            """

            returnStr = self.config.useConf(arg)
            return returnStr

        def showlog(self, arg):
            """
            Show various logs captured
            """

            return moduleCoordinator.ModuleCoordinator().getErrors()

        #TODO
        def shutdown(self, arg):
            """
            Shutdown this server
            """

            self.moduleDirChange.stop()
            self.moduleDirChange.join()
            moduleCoordinator.ModuleCoordinator().stopAll()
            if self.haleConf.get("xmpp", "use") == 'True':
                producerBot.ProducerBot().disconnectBot()
            sys.exit(0)
    
    haleConf = configHandler.ConfigHandler().loadHaleConf()
    port = int(haleConf.get("server", "port"))
    listen = haleConf.get("server", "listenhost")
    server_address = (listen, port)
    server = ServerClass(server_address, HandlerClass)    
    server.register_instance(xmlrpc_registers())    
    sa = server.socket.getsockname()
    print "\nServing XML-RPC over HTTPS on", sa[0], "port", sa[1]
    server.serve_forever()

if __name__ == '__main__':
    main()

