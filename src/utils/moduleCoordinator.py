################################################################################
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

import Queue, os
import threading, time, datetime
from utils import logHandler
from threading import Lock
from xmpp import producerBot
from conf import configHandler

import GeoIP
from django.db import IntegrityError
from webdb.hale.models import Botnet

class synchronized(object):
    """ 
    Class enapsulating a lock and a function
    allowing it to be used as a synchronizing
    decorator making the wrapped function
    thread-safe 
    """
    
    def __init__(self, *args):
        self.lock = Lock()
        
    def __call__(self, f):
        def lockedfunc(*args, **kwargs):
            try:
                self.lock.acquire()
                try:
                    return f(*args, **kwargs)
                except Exception, e:
                    raise
            finally:
                self.lock.release()

        return lockedfunc

class Singleton(type):
    """
    Singleton pattern used to only create one 
    ModuleCoordinator instance
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
        
LOG_EVENT = 0
START_EVENT = 1
URL_EVENT = 2
RELIP_EVENT = 3

class EventHolder(object):
    """
    Holds an event
    """
    
    def __init__(self, eventType, data, hash='', config=None):
        """
        Constructor
        """
        
        self.eventType = eventType
        self.data = data
        self.hash = hash
        self.config = config
        
    def getType(self):
        """
        Return event type
        """
        
        return self.eventType
        
    def getData(self):
        """
        Return contents of an event
        """
        
        return self.data
        
    def getHash(self):
        """
        Returns hash of config if event
        is a START_EVENT
        """
        
        return self.hash
        
    def getConfig(self):
        """
        Returns the config used by the module
        if the event is a LOG_EVENT
        """
        
        return self.config
        
class ModuleCoordinator(threading.Thread):
    """
    Handles module coordination: starting/stopping
    modules, collecting logs and errors
    """
    
    __metaclass__ = Singleton
    
    def __init__(self, haleConf):
        """
        Constructor, create list to hold modules that are
        running
        """
       
        self.haleConf = haleConf
        self.configHashes = {}
        self.modules = {}
        self.errors = list()
        self.events = list()
        self.runEventListener = True
        self.log = logHandler.LogHandler()
        self.url = logHandler.URLCheck()
        self.relip = logHandler.CCRelatedIP()
        geodata = os.getcwd() + "/utils/GeoIP.dat"
        if os.name == "nt":
            geodata = geodata.replace("/", "\\")
        self.geo = GeoIP.open(geodata, GeoIP.GEOIP_STANDARD)
        threading.Thread.__init__(self)
        
    def run(self):
        """
        Handle external events, i.e events
        not from CLI interaction
        """
        
        while self.runEventListener:
            if self.events:
                ev = self.events.pop()
                if ev.getType() == START_EVENT:
                    from modules import moduleManager
                    moduleManager.executeExternal(ev.getData()['module'], 'external_' + str(len(self.modules) + 1), ev.getData(), ev.getHash())
                if ev.getType() == LOG_EVENT:
                    self.log.handleLog(ev.getData(), ev.getHash(), ev.getConfig())
                if ev.getType() == URL_EVENT:
                    self.url.handleData(ev.getData(), ev.getHash(), ev.getConfig())
                if ev.getType() == RELIP_EVENT:
                    self.relip.handleIPs(ev.getData(), ev.getHash())
                
    def addEvent(self, eventType, data, hash='', config=None):
         """
         Add an event to the list
         """
         
         self.events.append(EventHolder(eventType, data, hash, config))
    
    def add(self, moduleExe, moduleId, hash, external=False):
        """
        Add a module to the list and start it,
        this method is called both on external events
        and from CLI interaction
        """
        
        if moduleId in self.modules:
            print "[ModuleCoordinator]: Id already used, choose another"
            return
            
        if self.haleConf.get("xmpp", "use") == 'True':
            monitored = producerBot.ProducerBot().getMonitoredBotnets()
            botnet = moduleExe.getConfig()['botnet']
            if not external and monitored != None:
                if hash in monitored or producerBot.ProducerBot().sendTrackReq(hash):
                    self.putError("Botnet: " + hash + " already monitored")
                    return
                
        self.modules[moduleId] = moduleExe
        self.configHashes[moduleId] = hash
        conf = self.modules[moduleId].getConfig()
        coord = self.geo.record_by_name(conf['botnet'])
        
        if coord == None:
            self.putError("Unkown host: " + conf['botnet'])
            self.modules.pop(moduleId)
            self.configHashes.pop(moduleId)
            return

        moduleExe.run()              
                
    @synchronized()
    def putError(self, exception, module=None):
        """
        Stores an error/exception into the list, this
        will info will be available when issuing a showlog
        in the CLI
        """
        
        now = datetime.datetime.now()
        logMsg = "[" + str(now.date()) + " " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + "]: " + exception
        if module != None:
            for key, value in self.modules.items():
                if value == module:
                    self.errors.append(logMsg)
                    self.stop(key)
                    return
        else:
            self.errors.append(logMsg)
               
    def getErrors(self):
        """
        Get error from the exception list. This list
        stores all exceptions from the different modules
        and the monitor program.
        """
        
        errors = ""
        if len(self.errors) == 0:
            return errors
        for error in self.errors:
            errors += error + "\n"
        return errors
        
    def stop(self, moduleId):
        """
        Stop a module with id moduleId
        """
        
        if moduleId not in self.modules.keys():
            return "No such id running"
        if self.haleConf.get("xmpp", "use") == 'True':
            producerBot.ProducerBot().removeBotnet(self.configHashes[moduleId])
        self.configHashes.pop(moduleId)
        self.modules[moduleId].stop()
        self.modules.pop(moduleId)
        
    def getAll(self):
        """
        Outputs all modules currently executed and their id
        """
        
        return self.modules.keys()

    def getInfo(self, moduleId):
        """
        Return hash of botnet monitored by module identified by moduleId
        """

        try:
            conf = self.modules[moduleId].getConfig()
        except KeyError:
            return ""
        confStr = configHandler.ConfigHandler().getStrFromDict(conf, toDB=True)
        return configHandler.ConfigHandler().getHashFromConfStr(confStr, toDB=False)[0]
        
    def stopAll(self):
        """
        Stop all modules, used on program termination
        """
        
        for ident in self.modules.keys():
            self.modules[ident].stop()
        self.runEventListener = False
        self.join()
            
