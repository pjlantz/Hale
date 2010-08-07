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

from haystack.indexes import *
from haystack import site
from webdb.hale.models import Botnet, File, RelatedIPs

class BotnetIndex(SearchIndex):
    """
    Botnet indexing
    """
    
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """
        Used when the entire index for model is updated
        """
        
        return Botnet.objects.all()

site.register(Botnet, BotnetIndex)

class FileIndex(SearchIndex):
    """
    File indexing (malware)
    """
    
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """
        Used when the entire index for model is updated
        """
        
        return File.objects.all()

site.register(File, FileIndex)

class RelatedIPsIndex(SearchIndex):
    """
    IP indexing
    """
    
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """
        Used when the entire index for model is updated
        """
        
        return RelatedIPs.objects.all()

site.register(RelatedIPs, RelatedIPsIndex)
