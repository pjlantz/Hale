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

import threading, sys
import re, urllib, hashlib, os

class URLHandler(threading.Thread):
    """
    Util class to check for urls and download possible 
    malwares through http proxies to hide the location
    """

    def __init__(self, config, data):
        """
        Constructor, fetch the url regexp and file extension
        configurations to download
        """
        
        self.data = data
        self.url_expre = re.compile(config['url_regexp'])
        self.extensions = self.__striplist(config['file_ext'].split(','))
        threading.Thread.__init__ (self)
        
    def run(self):
        """
        Check if data contains any url
        """
        
        match = self.url_expre.findall(self.data)
        if match:
            for entry in match:
                url = entry[0]
                fileposition = url.rfind('/')
                extfilename = url[fileposition + 1:]
                pos = url.rfind('.')
                extension = url[pos:].split('.')[1]
                if extension in self.extensions:
                    self.__doDownload(url, extfilename)
        
    def __doDownload(self, url, extfilename):
        """
        Download possible malware
        """
        
        proxies = {'http': 'http://174.142.104.57:3128'} # fetch from a list later
        opener = urllib.FancyURLopener(proxies)
        fp = opener.open(url)
        content = "".join(fp.readlines())
        fp.close()
        try:
            os.remove(tmp_file)
        except:
            pass
        md5 = hashlib.new('md5')
        hash = md5.update(content)
        fname = md5.hexdigest()
        filename = "%s-%s" % (fname, extfilename)
        if not os.path.exists(filename):
            fp = open(filename, 'a+')
            fp.write(content)
            fp.close()
            
    def __striplist(self, l):
        """
        Strip whitespaces from elements in a list
        """
        
        return([x.strip() for x in l])

