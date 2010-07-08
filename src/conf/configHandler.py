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

import sys, os
from ConfigParser import *

class Singleton(type):
    """
    Singleton pattern used to only create one 
    ConfigHandler instance
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
 
class ConfigHandler(object):
    """
    Parses configuration files
    """
    
    __metaclass__ = Singleton
    
    def __init__(self):
        """
        Constructor, create parser
        """
       
        self.currentConfig = ConfigParser()
        self.currentConfigFile = "conf/modules.conf"
        if os.name == "nt":
            self.currentConfigFile = self.currentConfigFile.replace("/", "\\")
        self.currentSection = ""
        self.current = {}
        
    def loadXMPPConf(self):
        """
        Load configs for XMPP and return them
        """
        
        self.xmppFile = "conf/hale.conf"
        if os.name == "nt":
            self.xmppFile = self.xmppFile.replace("/", "\\")
        self.xmppConf = ConfigParser()
        self.xmppConf.read(self.xmppFile)
        
        return self.xmppConf
       
    def listConf(self):
        """
        List all configurations
        """

        tabs = ""
        self.currentConfig = ConfigParser()
        self.currentConfig.read(self.currentConfigFile)
        lsStr = "\nConfig name\tFor module\n==========================\n"
        try:
            for section in self.currentConfig.sections():
                if len(section) <= 7:
                    tabs = "\t\t"
                else:
                    tabs = "\t"
                lsStr += section + tabs + "[" + self.currentConfig.get(section, "module") + "]\n"
        except Exception:
            print "[ConfigHandler]:", sys.exc_info()[1]
            return
        print lsStr
            
    def useConf(self, section):
        """
        Set config name 'section' to be used
        """
        
        if len(section) == 0:
            if len(self.currentSection) == 0:
                print "[ConfigHandler]: No config loaded "
            else:
                print "[ConfigHandler]: Using " + self.currentSection
            return
        
        self.currentConfig = ConfigParser()
        self.currentConfig.read(self.currentConfigFile)
        try:
            for option in self.currentConfig.options(section):
                self.current[option] = self.currentConfig.get(section, option)
        except NoSectionError:
            print "[ConfigHandler]: No such config " + section
            return
        self.currentSection = section
        print "[ConfigHandler]: Using " + section
        
    def getConfig(self):
        """
        Return the current config
        """
        
        return self.current
        
    def correctConfig(self, module):
        """
        Check if current config is correct to use
        with module named 'module'
        """

        self.currentConfig = ConfigParser()
        self.currentConfig.read(self.currentConfigFile)
        for section in self.currentConfig.sections():
            options = self.currentConfig.options(section)
            for option in options:
                if option == "module" and self.currentConfig.get(section, option) == module:
                    for opt in options:
                        try:
                            op = self.current[opt]
                        except KeyError:
                            print "[ConfigHandler]: Current config not for use with " + module
                            return False
        return True
                    