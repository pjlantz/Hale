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

from piston.handler import BaseHandler
from webdb.hale.models import Botnet, RelatedIPs, Log, File
from piston.utils import throttle


class BotnetHandler(BaseHandler):
    """
    Returns information about botnet(s)
    /api/botnet will reply with all botnets monitored
    /api/botnet/botnethash will reply with the botnet with hash equal to botnethash
    """
    
    allowed_methods = ('GET',)
    # fields in JSON reply
    fields = ('botnettype', 'host', 'longitude', 'latitude', 'botnethashvalue', 'config', 'firstseen', 'lastseen')
    model = Botnet
    
    @throttle(5, 1*60) # allow maximum 5 request per minute
    def read(self, request, hash):
        if len(hash) == 0:
            botnet = Botnet.objects.all()
        else:
            botnet = Botnet.objects.get(botnethashvalue=hash)
        return botnet
        
class BotnetHostHandler(BaseHandler):
    """
    Returns information about botnet(s) based on hostname
    /api/host/hostname will reply with all botnets monitored with host equal to hostname
    """
    
    methods_allowed = ('GET',)
    fields = ('botnettype', 'host', 'longitude', 'latitude', 'botnethashvalue', 'config', 'firstseen', 'lastseen')
    model = Botnet
    
    @throttle(5, 1*60)
    def read(self, request, hostname):
        botnet = Botnet.objects.filter(host=hostname) 
        return botnet
        
class BotnetTypeHandler(BaseHandler):
    """
    Returns information about botnet(s) based on module used
    /api/type/module will reply with all botnets monitored with the module
    """
    
    methods_allowed = ('GET',)
    fields = ('botnettype', 'host', 'longitude', 'latitude', 'botnethashvalue', 'config', 'firstseen', 'lastseen')
    model = Botnet
    
    @throttle(5, 1*60)
    def read(self, request, module):
        botnet = Botnet.objects.filter(botnettype=module) 
        return botnet
        
class BotnetIPsHandler(BaseHandler):
    """
    Returns information about botnet(s)
    /api/botips/hash will reply with all ips captured by botnet with the value hash
    """
    
    allowed_methods = ('GET',)
    fields = ('ip', '')
    model = RelatedIPs
    
    @throttle(5, 1*60)
    def read(self, request, hash):
        botnet = Botnet.objects.get(botnethashvalue=hash)
        ips = RelatedIPs.objects.filter(botnet=botnet.id)
        return ips
        
class BotnetLogsHandler(BaseHandler):
    """
    Returns information about botnet(s)
    /api/bologs/hash will reply with all logs for botnet with value hash
    """
    
    methods_allowed = ('GET',)
    fields = ('logdata', 'datetime')
    model = Log
    
    @throttle(5, 1*60)
    def read(self, request, hash):
        botnet = Botnet.objects.get(botnethashvalue=hash)
        logs = Log.objects.filter(botnet=botnet.id)
        return logs
       
class BotnetFilesHandler(BaseHandler):
    """
    Returns information about botnet(s)
    /api/bofiles/hash will reply with file hashes caputed by botnet with value hash
    """
    
    methods_allowed = ('GET',)
    fields = ('hash', '')
    model = File
    
    @throttle(5, 1*60)
    def read(self, request, hash):
        botnet = Botnet.objects.get(botnethashvalue=hash)
        files = File.objects.filter(botnet=botnet.id)
        return files
        
class FilesHandler(BaseHandler):
    """
    Returns information about botnet(s)
    /api/file/hash returns botnet(s) info for those that have captured file with the hash specified
    """
       
    methods_allowed = ('GET',)
    fields = ('botnettype', 'host', 'longitude', 'latitude', 'botnethashvalue', 'config', 'firstseen', 'lastseen')
    model = Botnet
    
    @throttle(5, 1*60)
    def read(self, request, hash):
        file = File.objects.get(hash=hash)
        botnet = Botnet.objects.filter(id=file.botnet.id)
        return botnet     
        
class IPHandler(BaseHandler):
    """
    Returns information about botnet(s)
    /api/ip/addr will reply with botnet(s) info for those that have detected an IP with number addr
    """
    
    methods_allowed = ('GET',)
    fields = ('botnettype', 'host', 'longitude', 'latitude', 'botnethashvalue', 'config', 'firstseen', 'lastseen')
    model = Botnet
    
    @throttle(5, 1*60)
    def read(self, request, ip):
        ip = RelatedIPs.objects.get(ip=ip)
        botnet = Botnet.objects.filter(id=ip.botnet.id)
        return botnet
        
                