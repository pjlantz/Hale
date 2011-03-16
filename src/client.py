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

import xmlrpclib, socket
import cmd, sys, os, getpass

from conf import configHandler

class CLI(cmd.Cmd):
    """
    Handles command line input with support for 
    command line completion and command history. 
    Additionally the cmd module provides a nice help feature,
    the comments for the do_command functions are shown 
    when issuing help <command>
    """
	
    def __init__(self):
        """
        Constructor, sets up cmd variables and other
        data structures holding modules, configs etc.
        Starts a manager thread taking care of newly
        added modules and errors from module threads
        """
        
        cmd.Cmd.__init__(self)

        print  " __  __            ___ "            
        print  "/\ \/\ \          /\_ \\"            
        print  "\ \ \_\ \     __  \//\ \      __"   
        print  " \ \  _  \  /'__`\  \ \ \   /'__`\\" 
        print  "  \ \ \ \ \/\ \L\.\_ \_\ \_/\  __/" 
        print  "   \ \_\ \_\ \__/.\_\/\____\ \____\\"
        print  "    \/_/\/_/\/__/\/_/\/____/\/____/\n"

        self.prompt = ">> "
        self.intro = "\nType help or '?' for a list of commands\n"
        self.conf = configHandler.ConfigHandler().loadHaleConf()
        host = self.conf.get("client", "server")
        port = self.conf.get("client", "port")
        self.config = configHandler.ConfigHandler()

        while True:
            self.user = raw_input("login: ")
            passwd = getpass.getpass(prompt="password: ")
            host = self.conf.get("client", "server")
            port = self.conf.get("client", "port")
            url = "http://" + self.user + ":" + passwd + "@" + host + ":" + port
            self.config = configHandler.ConfigHandler()
            self.proxy = xmlrpclib.ServerProxy(url)
            try:
                self.proxy.auth("")
            except xmlrpclib.ProtocolError:
                print "Incorrect login/password\n"
                continue
            except socket.error:
                print "Incorrect login/password\n"
                continue
            break

    def do_exec(self, arg):
        """
        Execute a module with the current config. 
        Usage: exec modulename identifier
        """
        
        config = self.config.getConfig()
        configHash = self.config.getCurrentHash()
        try:
            response = self.proxy.execmod(arg, config, configHash)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"
        
    def do_stop(self, arg):
        """
        Stops a module identified by id
        Usage: stop id
        """
        
        try:
            response = self.proxy.stopmod(arg)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"
    
    def do_lsmod(self, arg):
        """
        List all modules currently installed
        """
        
        try:
            response = self.proxy.lsmod(arg)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"
            
    def do_lsexec(self, arg):
        """
        List all modules being executed at the moment
        """
        
        try:
            response = self.proxy.lsexec(arg)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"

    def do_execinfo(self, arg):
        """
        List info about executing module
        Usage: execinfo id
        """

        try:
            response = self.proxy.execinfo(arg)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"
            
    def do_lsconf(self, arg):
        """
        List all configurations
        """

        print self.config.listConf()      
        
    def do_reload(self, arg):
        """
        Reload a module if changes have been made to it
        Usage: reload modulename
        """
        
        try:
            response = self.proxy.reloadmod(arg)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"
        
    def do_useconf(self, arg):
        """
        Set the current config to use, if argument
        is empty, current config used is printed out
        """
        
        print self.config.useConf(arg)
        
    
    def default(self, line):
        """
        Called when command input is not recognized
        and outputs an error message
        """
        
        print "Unkown command: " + line
        
    def emptyline(self):
        """
        Called when empty line was entered at the prompt
        """
        
        pass

    def do_showlog(self, arg):
        """
        Show recent logs from the monitor
        and the modules
        """
        
        try:
            response = self.proxy.showlog(arg)
            print response
        except xmlrpclib.ProtocolError:
            print "Operation denied"
        
    def do_quit(self, arg):
        """
        Exit the program gracefully
        """
        
        self.do_exit(arg)
        
    def do_exit(self, arg):
        """
        Exit the program gracefully
        """
        
        print "Bye!"
        sys.exit(0)

if __name__ == "__main__":
    """
    Main program starts
    """

    CLI().cmdloop()

