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
    
    host = models.CharField(max_length=100)
    port = models.IntegerField()
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class Log(models.Model):
    """
    Keeps all logs
    """
    
    botnetid = models.CharField(max_length=100)

class Botnet(models.Model):
    """
    Keeps botnet details
    """
    
    host = models.CharField(max_length=100)

class Module(models.Model):
    """
    Keeps the module source and config examples
    """
    
    module = models.CharField(max_length=100)
    conf = models.CharField(max_length=100)

class Files(models.Model):
    """
    Holds the analysis URL from the sandbox submitted to
    """
    
    analysisURL = models.CharField(max_length=100)