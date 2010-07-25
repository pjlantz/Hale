# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Botnet.longitude'
        db.add_column('hale_botnet', 'longitude', self.gf('django.db.models.fields.FloatField')(default=0), keep_default=False)

        # Adding field 'Botnet.latitude'
        db.add_column('hale_botnet', 'latitude', self.gf('django.db.models.fields.FloatField')(default=0), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'Botnet.longitude'
        db.delete_column('hale_botnet', 'longitude')

        # Deleting field 'Botnet.latitude'
        db.delete_column('hale_botnet', 'latitude')
    
    
    models = {
        'hale.botnet': {
            'Meta': {'object_name': 'Botnet'},
            'botnettype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'config': ('django.db.models.fields.TextField', [], {}),
            'firstseen': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastseen': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {})
        },
        'hale.file': {
            'Meta': {'object_name': 'File'},
            'analysisurl': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'botnet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hale.Botnet']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hale.log': {
            'Meta': {'object_name': 'Log'},
            'botnet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hale.Botnet']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logdata': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hale.module': {
            'Meta': {'object_name': 'Module'},
            'confexample': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'modulename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'hale.proxy': {
            'Meta': {'object_name': 'Proxy'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }
    
    complete_apps = ['hale']
