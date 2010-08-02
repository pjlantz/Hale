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

from django.db import models

class Proxy(models.Model):
    """
    Holds proxy host and credentials
    """
    
    host = models.CharField(max_length=32)
    port = models.IntegerField()
    user = models.CharField(max_length=32)
    password = models.CharField(max_length=32)

class Log(models.Model):
    """
    Keeps all logs
    """
    
    botnet = models.ForeignKey('Botnet')
    datetime = models.DateTimeField(auto_now=True)
    logdata = models.CharField(max_length=1024)

class Botnet(models.Model):
    """
    Keeps botnet details
    """
    
    # hash value of the unique keys from the config
    botnethashvalue = models.CharField(max_length=32, unique=True)
    # irc, http etc.
    botnettype = models.CharField(max_length=32)
    host = models.CharField(max_length=100)
    # configuration used
    config = models.TextField()
    firstseen = models.DateTimeField(auto_now_add=True)
    lastseen = models.DateTimeField(auto_now=True)
    longitude = models.FloatField()
    latitude = models.FloatField()

class Module(models.Model):
    """
    Keeps the module source and config examples
    """
    
    modulename = models.CharField(max_length=32, unique=True)
    filename = models.CharField(max_length=32)
    module = models.FileField(upload_to='modules')
    # configuration example for this module
    confexample = models.TextField()
    
class RelatedIPs(models.Model):
    """
    Used to keep track of ips related to a specific
    botnet
    """
    
    botnet = models.ForeignKey('Botnet')
    ip = models.IPAddressField(unique=True)

class File(models.Model):
    """
    Holds the file and analysis URL for the sandbox 
    submitted to together with details about the file
    """
    
    botnet = models.ForeignKey('Botnet')
    hash = models.CharField(max_length=32, unique=True)
    content = models.TextField()
    filename = models.CharField(max_length=100)
    