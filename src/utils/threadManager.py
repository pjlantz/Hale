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
        
    def add(self, moduleThread, threadId):
        """
        Add a thread to the list and start it
        """
        
        if threadId in self.threads:
            print "[ThreadManager]: Id already used, choose another"
            return
        
        self.threads[threadId] = moduleThread
        moduleThread.start()
        
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
            