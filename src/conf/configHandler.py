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

import sys, os, hashlib
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
       
        self.currentHash = ''
        self.currentConfig = ConfigParser()
        self.currentConfigFile = "conf/modules.conf"
        self.currentConfig.read(self.currentConfigFile)
        self.currentSection = ''
        self.current = {}
        
    def loadHaleConf(self):
        """
        Load configs for Hale and return them
        """
        
        self.confFile = "conf/hale.conf"
        self.haleConf = ConfigParser()
        self.haleConf.read(self.confFile)
        
        return self.haleConf
       
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
                if section != 'uniqueKeys':
                    if len(section) <= 7:
                        tabs = "\t\t"
                    else:
                        tabs = "\t"
                    lsStr += section + tabs + "[" + self.currentConfig.get(section, "module") + "]\n"
        except Exception:
            return "[ConfigHandler]:", sys.exc_info()[1]
        return lsStr
            
    def useConf(self, section):
        """
        Set config name 'section' to be used
        """
        
        if len(section) == 0 or section == 'uniqueKeys':
            if self.currentSection == '':
                return "[ConfigHandler]: No config loaded "
            return "[ConfigHandler]: Using " + self.currentSection
    
        self.currentConfig = ConfigParser()
        self.currentConfig.read(self.currentConfigFile)
        
        try:
            for option in self.currentConfig.options(section):
                self.current[option] = self.currentConfig.get(section, option)
        except NoSectionError:
            return "[ConfigHandler]: No such config " + section
    
        try:
            dict = self.current
            dictStr = self.getStrFromDict(dict)
            md5 = hashlib.new('md5')
            md5.update(dictStr.strip())
            self.currentHash = md5.hexdigest()
        except NoSectionError:
            return '[ConfigHandler]: uniqueKeys section missing'
        self.currentSection = section
        return "[ConfigHandler]: Using " + section
            
    def getHashFromConfStr(self, confStr, toDB=False):
        """
        Get the hash value of the config,
        used by the producer bot
        """
        
        moduleError = False
        dict = self.getDictFromStr(confStr)
        if not toDB:
            moduleError = self.__checkModule(dict)
            if moduleError:
                return '', moduleError
        dictStr = self.getStrFromDict(dict, True)
        md5 = hashlib.new('md5')
        if not dictStr:
            return "", True
        md5.update(dictStr.strip())
        return md5.hexdigest(), moduleError
        
    def __checkModule(self, conf):
        """
        Check if module is supported, used
        on external event
        """
        
        if conf:
            module = conf['module']
            from modules import moduleManager
            if module in moduleManager.get_modules():
                return False
            return True
        
    def getStrFromDict(self, dict, external=False, toDB=False):
        """
        Returns a string from a dictionary with
        only unique keys, or all keys if toDB is set
        to True
        """
        
        dictStr = ''
        if toDB:
            for key in dict.iterkeys():
                dictStr += key + '=' + dict[key] + ' '
            return dictStr.strip()
        items = None
        if not dict:
            return
        if external:
            items = dict.items()
        unique = self.getUniqueKeys(dict['module'].strip(), items)
        for key in sorted(unique.iterkeys()):
            dictStr += key + '=' + dict[key] + ' '
        return dictStr.strip()

        
    def getDictFromStr(self, string):
        """
        Returns a dictionary with configs
        from a string
        """
    
        dict = {}
        previousKey = ''
        stringList = string.strip().split(' ')
        for config in stringList:
            key = config.split('=')[0]
            try:
                value = config.split('=')[1]
            except IndexError:
                try:
                    newValue = dict[previousKey].strip()
                    newValue = newValue + ' ' + key.strip()
                    dict[previousKey] = newValue
                    continue
                except KeyError:
                    return
            previousKey = key
            dict[key] = value.strip()
        return dict
        
    def getUniqueKeys(self, module, current=None):
        """
        Fetches only unique keys specified in the config
        from a module named 'module'
        """
    
        uniqueDict = {}
        uniques = self.__striplist(self.currentConfig.get('uniqueKeys', module).split(','))
        items = self.current.items()
        for unique in uniques:
            if '*' in unique:
                unique = unique.split('*')[1].strip()
            if current != None:
                items = current
            for (key, value) in items:
                if unique in key:
                    uniqueDict[key] = value
                    
        return uniqueDict
            
    def getCurrentHash(self):
        """
        Returns hash for current config used
        """
        
        return self.currentHash
        
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
                            error = "[ConfigHandler]: Current config not for use with " + module
                            return (False, error)
        return (True, "")
        
    def __striplist(self, l):
        """
        Strip whitespaces from elements in a list
        """
        
        return([x.strip() for x in l])
                    
