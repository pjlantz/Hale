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

import cmd, sys

class CLI(cmd.Cmd):
    """
    Handles command line input
    """
	
    # default prompt
    prompt = ">> "
    
    def default(self, line):
        """
        Called when command input is not recognized
        and outputs an error message
        """
        print "Unkown command: " + line
        
    def do_quit(self, arg):
        """
        Exit the program
        """
        sys.exit(0)
        
    def do_exit(self, arg):
        """
        Exit the program
        """
        sys.exit(0)

if __name__ == "__main__":
    def start_cmd(banner=""):
        """
        Used to prevent CTRL+C signals to interrupt the program.
        SIGINT does not work on Windows and neither does
        SetConsoleCtrlHandler from win32api together with the cmd
        module
        """
        try:
            CLI().cmdloop(banner)
        except KeyboardInterrupt:
            print "\r"
            start_cmd()

    start_cmd("\nType help for a list of commands\n")
            

