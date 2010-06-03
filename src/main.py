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

import cmd, sys, os, signal
if os.name == "nt":
    try:
        import pyreadline
    except ImportError:
        print "Error: Windows PyReadline support missing"
        sys.exit(1)

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
        Constructor, sets up cmd variables
        """
        cmd.Cmd.__init__(self)
        self.prompt = ">> "
        self.intro = "\nType help for a list of commands\n"
        self.undoc_header = "Help commands available:"
    
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
        
    def do_quit(self, arg):
        """
        Exit the program gracefully
        """
        self.do_exit(arg)
        
    def do_exit(self, arg):
        """
        Exit the program gracefully
        """
        sys.exit(0)

def set_ctrlc_handler(func):
    """
    Catch CTRL+C and let the function
    on_ctrlc take care of it
    """
    signal.signal(signal.SIGINT, func)

if __name__ == "__main__":
    """
    Main program starts
    """
    def on_ctrlc(sig, func=None):
        """
        Ignore pressed CTRL+C
        """
        pass

    set_ctrlc_handler(on_ctrlc)
    CLI().cmdloop()
            

