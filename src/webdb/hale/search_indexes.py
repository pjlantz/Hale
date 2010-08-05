from haystack.indexes import *
from haystack import site
from hale.models import Botnet, File, RelatedIPs

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
