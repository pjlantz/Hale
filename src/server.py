#############################################################################
#   (c) 2011, The Honeynet Project
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

import socket, os, base64, xmlrpclib
import sys, signal, threading, time
from twisted.web import xmlrpc, server, http
from twisted.internet import defer, protocol

os.environ["DJANGO_SETTINGS_MODULE"] = "webdb.settings"
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from conf import configHandler
from modules import moduleManager
from utils import moduleCoordinator
from xmpp import producerBot
from ConfigParser import *
        
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
    
class Server(xmlrpc.XMLRPC):
        """
        XML-RPC instance with methods to be called
        """

        def __init__(self):
            """
            Constructor to set up objects to be used
            """

            self.allowNone = True
            self.useDateTime = False
            moduleManager.handle_modules_onstart()
            self.haleConf = configHandler.ConfigHandler().loadHaleConf()
            moduleCoordinator.ModuleCoordinator(self.haleConf).start()
            if self.haleConf.get("xmpp", "use") == 'True':
                producerBot.ProducerBot(self.haleConf).run()
            self.moduleDirChange = ModuleDirChangeThread()
            self.moduleDirChange.start()
            self.config = configHandler.ConfigHandler()
            self.modlist = []

        def xmlrpc_auth(self, arg):
            """
            Used to check authentication
            """
            
            return ""

        def xmlrpc_lsmod(self, arg):
            """
            Return all installed modules
            """

            lsStr = "\nInstalled modules\n=================\n"
            self.modlist = moduleManager.get_modules()
            for mod in self.modlist:
                lsStr += mod + "\n"
            return lsStr

        def xmlrpc_execmod(self, arg, config, configHash):
            """
            Start a module
            """

            args = arg.split(' ')
            if len(args) < 2:
                return "Usage: exec modulename identifier"
            errorStr = moduleManager.execute(args[0], args[1], config, configHash)
            if errorStr != None:
                return errorStr
            return args[1] + " started"

        def xmlrpc_stopmod(self, arg):
            """
            Stop a specific module
            """

            errorStr = moduleCoordinator.ModuleCoordinator().stop(arg)
            if errorStr != None:
                return errorStr
            return arg + " is now being stopped"

        def xmlrpc_lsexec(self, arg):
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

        def xmlrpc_execinfo(self, arg):
            """
            Return info about modules running
            """

            info = moduleCoordinator.ModuleCoordinator().getInfo(arg)
            if len(info) == 0:
                return "No such id running"
            infoStr = "\nModule ID\tHash\n=========\t=================\n"
            infoStr += arg + "\t" + info + "\n"
            return infoStr

        def xmlrpc_reloadmod(self, arg):
            """
            Reload a module file
            """

            errorStr = moduleManager.reload_module(arg)
            if errorStr != None and len(errorStr) > 0:
                return errorStr
            return arg + " reloaded"

        def xmlrpc_showlog(self, arg):
            """
            Show various logs captured
            """

            return moduleCoordinator.ModuleCoordinator().getErrors()

        def render(self, request):
            """ 
            Overridden 'render' method which takes care of
            HTTP basic authorization 
            """
        
            user = request.getUser()
            passwd = request.getPassword()
            if user == '' and passwd == '':
                request.setResponseCode(http.UNAUTHORIZED)
                return 'Authorization required!'
            else:
                try:
                    u = User.objects.get(username__exact=user)
                except User.DoesNotExist:
                    request.setResponseCode(http.UNAUTHORIZED)
                    return 'Authorization Failed!'
                if u.check_password(passwd) and u.is_staff == True:
                    pass
                else:
                    request.setResponseCode(http.UNAUTHORIZED)
                    return 'Authorization Failed!'

            request.content.seek(0, 0)
            (args, functionPath) = xmlrpclib.loads(request.content.read())
            try:
                function = self._getFunction(functionPath)
            except xmlrpclib.Fault, f:
                self._cbRender(f, request)
            else:
                request.setHeader("content-type", "text/xml")
                defer.maybeDeferred(function, *args).addErrback(self._ebRender).addCallback(self._cbRender, request)
            return server.NOT_DONE_YET


if __name__ == '__main__':
    from twisted.internet import reactor
    s = Server()
    conf = configHandler.ConfigHandler().loadHaleConf()
    port = int(conf.get("server", "port"))
    reactor.listenTCP(port, server.Site(s))
    reactor.run()

