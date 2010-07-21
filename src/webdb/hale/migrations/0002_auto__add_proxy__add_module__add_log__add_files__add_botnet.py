# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Proxy'
        db.create_table('hale_proxy', (
            ('user', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('hale', ['Proxy'])

        # Adding model 'Module'
        db.create_table('hale_module', (
            ('conf', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('hale', ['Module'])

        # Adding model 'Log'
        db.create_table('hale_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('botnetid', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('hale', ['Log'])

        # Adding model 'Files'
        db.create_table('hale_files', (
            ('analysisURL', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hale', ['Files'])

        # Adding model 'Botnet'
        db.create_table('hale_botnet', (
            ('host', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hale', ['Botnet'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Proxy'
        db.delete_table('hale_proxy')

        # Deleting model 'Module'
        db.delete_table('hale_module')

        # Deleting model 'Log'
        db.delete_table('hale_log')

        # Deleting model 'Files'
        db.delete_table('hale_files')

        # Deleting model 'Botnet'
        db.delete_table('hale_botnet')
    
    
    models = {
        'hale.botnet': {
            'Meta': {'object_name': 'Botnet'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hale.files': {
            'Meta': {'object_name': 'Files'},
            'analysisURL': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hale.log': {
            'Meta': {'object_name': 'Log'},
            'botnetid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hale.module': {
            'Meta': {'object_name': 'Module'},
            'conf': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hale.proxy': {
            'Meta': {'object_name': 'Proxy'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['hale']
