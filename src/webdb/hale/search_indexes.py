from haystack.indexes import *
from haystack import site
from hale.models import Botnet, File, RelatedIPs

class BotnetIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """
        Used when the entire index for model is updated
        """
        
        return Botnet.objects.all()

site.register(Botnet, BotnetIndex)

class FileIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """
        Used when the entire index for model is updated
        """
        
        return File.objects.all()

site.register(File, FileIndex)

class RelatedIPsIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    
    def get_queryset(self):
        """
        Used when the entire index for model is updated
        """
        
        return RelatedIPs.objects.all()

site.register(RelatedIPs, RelatedIPsIndex)
