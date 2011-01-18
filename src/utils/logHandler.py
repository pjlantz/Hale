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

import GeoIP
import sys, pefile, base64, socks
import re, urllib2, hashlib, os, socket
from twisted.internet import reactor
import proxySelector
from xmpp import producerBot
from conf import configHandler
from django.db import IntegrityError
from webdb.hale.models import Botnet, Log, File, RelatedIPs

class LogHandler(object):

    """
    Put logs to the XMPP share channel and database
    """
    
    def __init__(self):
        """
        Constructor
        """
        
        geodata = os.getcwd() + "/utils/GeoIP.dat"
        if os.name == "nt":
            geodata = geodata.replace("/", "\\")
        self.geo = GeoIP.open(geodata, GeoIP.GEOIP_STANDARD)
        self.haleConf = configHandler.ConfigHandler().loadHaleConf()
        
    def handleLog(self, data, botnethash, config):
        """
        Handles the log data by creating new thread for 
        database input and simply puts this data to the
        XMPP bot
        """
        
        reactor.callInThread(self.putToDB, data, botnethash, config)
        if self.haleConf.get("xmpp", "use") == 'True':
            self.putToXMPP(data, config, botnethash)
            
    def putToDB(self, data, botnethash, conf):
        """
        Creates new log entry in the database
        """

        confStr = configHandler.ConfigHandler().getStrFromDict(conf, toDB=True)
        coord = self.geo.record_by_name(conf['botnet'])
        b = Botnet(botnethashvalue=botnethash, botnettype=conf['module'], host=conf['botnet'], config=confStr, longitude=coord['longitude'], latitude=coord['latitude'])
        try:
            b.save()
        except IntegrityError:
            b = Botnet.objects.get(botnethashvalue=botnethash)
            b.longitude = coord['longitude']
            b.latitude = coord['latitude']
            b.save()
        
        botnetobject = Botnet.objects.get(botnethashvalue=botnethash)
        Log(botnet=botnetobject, logdata=data).save()
        botnetobject.save()
            
    def putToXMPP(self, data, config, botnethash):
        """
        Tell producer bot to output log message in the
        share channel
        """
        
        logmsg = '[' + botnethash + '] ' + data
        producerBot.ProducerBot().sendLog(logmsg)
        
class CCRelatedIP(object):
    """
    Store C&C related IP numbers
    """
    
    def __init__(self):
        pass
    
    def handleIPs(self, data, botnethash):
        """
        Fetch list of ips
        """
        
        try:
            ips = socket.gethostbyname_ex(data)
            reactor.callInThread(self.putToDB, ips, botnethash)
        except Exception:
            return
            
    def putToDB(self, ips, botnethash):
        """
        Put the ips found in the db
        """
        
        botnetobject = Botnet.objects.get(botnethashvalue=botnethash)
        ips = ips[2]
        for ip in ips:
            try:
                RelatedIPs(botnet=botnetobject, ip=ip).save()
            except IntegrityError:
                pass
        
class URLCheck(object):
    """
    Check for URL in data captured and do a possible
    download
    """

    def __init__(self):
        """
        Constructor sets up regular expression used to 
        find urls
        """
        
        self.prox = proxySelector.ProxySelector()
        self.url_expre = re.compile('((http|https|ftp)://[~@a-zA-Z0-9_\-/\\\.\+:]+)')
        
    def handleData(self, data, botnethash, config):
        """
        Compile the reg expression and fetch extensions.
        Check for regexp matches and if do download if 
        file extensions match.
        """
        
        self.botnethash = botnethash
        self.data = data
        
        match = self.url_expre.findall(self.data)
        if match:
            for entry in match:
                url = entry[0]
                fileposition = url.rfind('/')
                extfilename = url[fileposition + 1:]
                pos = url.rfind('.')
                try:
                    extension = url[pos:].split('.')[1]
                except IndexError:
                    pass
                reactor.callInThread(self.doDownload, url, extfilename)
                    
    def doDownload(self, url, extfilename):
        """
        Download file from captured url and check its
        PE header when downloaded.
        """
        
        proxyInfo = self.prox.getRandomProxy()
        if proxyInfo == None:
            pass
        else:
            if len(proxyInfo['USER']) == 0: 
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxyInfo['HOST'], proxyInfo['PORT'])
            else:
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxyInfo['HOST'], proxyInfo['PORT'], proxyInfo['USER'], proxyInfo['PASS'])
            socket.socket = socks.socksocket

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', '')]

        fp =  opener.open(url)
        urlinfo = fp.info()
        if "text/html" in urlinfo['Content-Type']: # no executable
            fp.close()
            return
        content = "".join(fp.readlines())
        fp.close()
        try:
            os.remove(tmp_file)
        except:
            pass
        md5 = hashlib.new('md5')
        hash = md5.update(content)
        fname = md5.hexdigest()
        filename = extfilename
        if os.name == "nt":
            filename = filename.replace("/", "\\")
        if not os.path.exists(filename):
            fp = open(filename, 'a+')
            fp.write(content)
            fp.close()
            try:
                pe = pefile.PE(filename, fast_load=True)
            except Exception:
                os.remove(filename)
                return
            os.remove(filename)
            content = base64.b64encode(content)
            producerBot.ProducerBot().sendFile(content, fname)
            botnetobject = Botnet.objects.get(botnethashvalue=self.botnethash)
            try:
                File(botnet=botnetobject, hash=fname, content=content, filename=filename).save()
                botnetobject.save()
            except IntegrityError:
                pass
        
