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
 
# stores all loaded modules and
# its function to be run on 'exec'
modules = {}
# stores modules filename
files = []

def register(module):
    """ 
    Decorator to be used for registering a function 'func' belonging 
    to a module that handles the configuration for that module
    """
    def registered_module(func):
        modules[module] = func
        return func
    return registered_module
 
def execute(module, config):
    """ 
    Call this function to execute a module with the configurations 'config'
    """
    if module not in modules:
        print "[Module manager]: No such module " + module
        return
    func = modules[module]
    try:
        func(config)
    except KeyError:
        print "[Module manager]: Wrong configuration file for module " + module
 
def load_modules(file):
    """ 
    Unload/Load modules from a file
    """
    tmpList = [] # temporary store all modules to check later for removed ones
    with open(file, "r") as fh:
        for line in fh:
            line = line.strip()
            tmpList.append(line)
            if line.startswith("#") or line == "":
                continue
            try:
                module = __import__(line,  globals(), locals(), [], -1)
                reload(module) # in case the module was unloaded before, needed to register again
            except ImportError:
                pass
         
            files.append(line)
            
    # Check for removed modules        
    for file in files:
        if file not in tmpList:
            files.remove(file)
            key = file.split("Module")[0]
            if modules.has_key(key):
                modules.pop(key)
            
def get_modules():
    """
    Return a list of loaded modules
    """
    return modules.keys()
    