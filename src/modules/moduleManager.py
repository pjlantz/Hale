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

import os, sys

# maps module names with registered functions
modules = {}
# stores modules filename
files = []
# stores modules
imports = {}
# modules with errors
errors = {}

moduleDir = os.getcwd() + "/modules/"
if os.name == "nt":
    moduleDir = moduleDir.replace("/", "\\")

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
        print "[ModuleManager]: No such module " + module
        return
    func = modules[module]
    try:
        func(config)
    except KeyError:
        print "[ModuleManager]: Wrong configuration file for module " + module
        
def handle_modules_onstart():
    """
    Remove old pyc files for the modules on start
    """
    
    content = os.listdir(moduleDir)
    for file in content:
        components = file.split(".pyc")
        name = components[0]
        if len(components) > 1:
            if "moduleManager" != name and "__init__" != name:
                os.remove(moduleDir + file)
    
def load_modules():
    """ 
    Load/Unload modules from the modules directory
    """ 
    
    error = False
    tmpList = [] # store temporarily module file to check for removed ones later 
    content = os.listdir(moduleDir)
    for file in content:
        tmpList.append(file)
        components = file.split("Module")
        if len(components) > 1:
            modName = components[0]
            if file not in files:
                check_module(file)
            if modName in modules or file in errors or components[1] == ".pyc":
                continue
            try:
                reload(imports[modName]) # reload module
            except KeyError: # no such modName module stored, import first time
                try:
                    module = __import__(file.split(".py")[0],  globals(), locals(), [], -1)
                    imports[modName] = module # store modules for reload later
                except ImportError:
                    pass
            files.append(file)
    
    # check for removed modules
    for file in files:
        if file not in tmpList:
            name = file.split(".py")[0]
            files.remove(file)
            os.remove(moduleDir + name + ".pyc") # remove pyc file if module has been removed
            key = file.split("Module")[0]
            if modules.has_key(key):
                modules.pop(key)
                
def check_module(file):
    """
    Check if module is correct, i.e register name
    is unique and the module follow the name convention
    nameModule.py and @moduleManager.register("name").
    Additionally check if moduleManager is imported
    """

    if os.path.splitext(file)[1] == ".pyc":
        return
    
    regName = ""
    foundError = False
    importError = False
    foundImport = False
    comment = False
    commentCount = 1
    with open(moduleDir + file, "r") as fh:
        for line in fh:
            if '"""' in line:
                comment = commentCount % 2
                commentCount += 1
            if "import moduleManager" in line:
                foundImport = True
                if "#" in line or comment:
                    importError = True
                    break
            if "@moduleManager.register" in line and "#" not in line and not comment:
                regName = line.split('"')[1]
                break
    
    errorMsg = ""
    if importError or not foundImport: # wrong import of module or none found at all
        errorMsg += "\n[ModuleManager]: Import of moduleManager not defined for " + file.split(".py")[0]
        foundError = True
    elif len(regName) == 0:
        errorMsg += "\n[ModuleManager]: Follow the module API for " + file.split(".py")[0]
        foundError = True
    else:   
        if regName in modules:
            errorMsg = "\n[ModuleManager]: Register name " + regName + " already in use, add unique for " + file.split(".py")[0]
            foundError = True
        if regName + "Module.py" != file:
            errorMsg += "\n[ModuleManager]: Please follow the name convention for " + file.split(".py")[0]
            foundError = True
    
    if file not in errors and foundError:
        print errorMsg
        
    if foundError:
        errors[file] = "" # set to anything
    else:
        try:
            errors.pop(file) # no errors, import module
        except KeyError:
            pass
            
def get_modules():
    """
    Return a list of loaded modules
    """
    
    return modules.keys()
    