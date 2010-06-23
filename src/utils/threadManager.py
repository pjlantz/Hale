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
from threading import Lock

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
    ThreadManager instance
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
        
class ThreadManager(object):
    """
    Handles execution and stopping of threads
    """
    
    __metaclass__ = Singleton
    
    def __init__(self):
        """
        Constructor, create list to hold thread objects
        """
       
        self.threads = {}
        self.bucket = Queue.Queue()
        
    def add(self, moduleThread, threadId):
        """
        Add a thread to the list and start it
        """
        
        if threadId in self.threads:
            print "[ThreadManager]: Id already used, choose another"
            return
        
        self.threads[threadId] = moduleThread
        moduleThread.start()
    
    @synchronized()
    def putError(self, exception, thread):
        """
        Stores an exception into the bucket
        """
        
        for key, value in self.threads.items():
            if value == thread:
                self.bucket.put(exception) # add more info later
                thread.doStop()
                self.threads.pop(key)
                return

        # exceptions from non-modules, eg. urlHandler 
        self.bucket.put(exception) # add more info later
        
    def getError(self):
        """
        Get error from the exception bucket. This bucket
        stores all exceptions from the different threads.
        """
        
        try:
            exc = self.bucket.get(block=False)
        except Queue.Empty:
            pass
        else:
            print "[ThreadManager]: ", exc
        
    def stop(self, threadId):
        """
        Stop a thread with id threadId
        """
        
        if threadId not in self.threads.keys():
            print "No such id running"
            return
        self.threads[threadId].doStop()
        self.threads[threadId].join()
        self.threads.pop(threadId)
        
    def getAll(self):
        """
        Outputs all modules currently executed and their id
        """
        
        return self.threads.keys()
        
    def stopAll(self):
        """
        Stop all threads, used on program termination
        """
        
        for ident in self.threads.keys():
            self.threads[ident].doStop()
            self.threads[ident].join()
            