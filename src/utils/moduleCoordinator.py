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

import Queue
import threading, time
from utils import logHandler
from twisted.internet import reactor
from threading import Lock
#from xmpp import producerBot

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
STOP_EVENT = 2

class EventHolder(object):
    """
    Holds an event
    """
    
    def __init__(self, eventType, data):
        """
        Constructor
        """
        
        self.eventType = eventType
        self.data = data
        
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
        
class Dispatcher(threading.Thread):
    """
    Runs the reactor loop outside
    main thread
    """
    
    def __init__(self):
        """
        Constructor
        """
        
        threading.Thread.__init__(self)

    def run(self):
        """
        Starts the reactor loop and then this
        thread finishes
        """
        
        reactor.run(installSignalHandlers=0)
        
class ModuleCoordinator(threading.Thread):
    """
    Handles module coordination: starting/stopping
    modules, collecting logs and errors
    """
    
    __metaclass__ = Singleton
    
    def __init__(self):
        """
        Constructor, create list to hold modules that are
        running
        """
       
        self.modules = {}
        self.dispatcherFirstStart = True
        self.bucket = Queue.Queue()
        self.events = list()
        self.runEventListener = True
        threading.Thread.__init__(self)
        
    def run(self):
        """
        Handle external events, i.e events
        not from CLI interaction
        """
        
        while self.runEventListener:
            if self.events:
                ev = self.events.pop()
                if ev.getType() == LOG_EVENT:
                    logHandler.LogHandler().handleLog(ev.getData())
                    print "From eventMonitor: " + ev.getData()
                
    def addEvent(self, eventType, data):
         """
         Add an event to the list
         """
         
         self.events.append(EventHolder(eventType, data))
    
    def add(self, moduleExe, moduleId):
        """
        Add a module to the list and start it,
        this method is called both on external events
        and from CLI interaction, the difference is that
        from CLI interaction this method is called directly
        """
        
        if moduleId in self.modules:
            print "[ModuleCoordinator]: Id already used, choose another"
            return
            
        monitored = list()
	    #monitored = producerBot.ProducerBot().getMonitoredBotnets()
        botnet = moduleExe.getConfig()['botnet']
        if botnet not in monitored:
	        #if not producerBot.ProducerBot().sendTrackReq(botnet):
                self.modules[moduleId] = moduleExe
                moduleExe.run()
                if self.dispatcherFirstStart:
                    Dispatcher().start()
                    self.dispatcherFirstStart = False
   	        #else:
                #print "Botnet already monitored!"
        else:
            print "You are already monitoring this!"
    
    @synchronized()
    def putError(self, exception, module=None):
        """
        Stores an error/exception into the bucket, this
        will info will be available when issuing a showlog
        in the CLI
        """
        
        if module != None:
	        for key, value in self.modules.items():
	            if value == module:
	                self.bucket.put(exception) # add more detailed info later, like time etc
	                self.stop(key)
	                return
        else:
            # exceptions from non-modules, eg. urlHandler 
            self.bucket.put(exception) # add more detailed info later, like time etc
               
    def getErrors(self):
        """
        Get error from the exception bucket. This bucket
        stores all exceptions from the different modules
        and the monitor program.
        """
        
        try:
		    while True:
		        print self.bucket.get_nowait()
        except Queue.Empty:
		    pass

        
    def stop(self, moduleId):
        """
        Stop a module with id moduleId
        """
        
        if moduleId not in self.modules.keys():
            print "No such id running"
            return
        #producerBot.ProducerBot().removeBotnet(self.threads[threadId].getConfig()['botnet'])
        self.modules[moduleId].stop()
        self.modules.pop(moduleId)
        
    def getAll(self):
        """
        Outputs all modules currently executed and their id
        """
        
        return self.modules.keys()
        
    def stopAll(self):
        """
        Stop all modules, used on program termination
        """
        
        for ident in self.modules.keys():
            self.modules[ident].stop()
        if not self.dispatcherFirstStart:
            reactor.stop()
        self.runEventListener = False
        self.join()
            