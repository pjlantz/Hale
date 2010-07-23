# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Proxy'
        db.create_table('hale_proxy', (
            ('user', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('hale', ['Proxy'])

        # Adding model 'Log'
        db.create_table('hale_log', (
            ('logdata', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('botnet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hale.Botnet'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('hale', ['Log'])

        # Adding model 'Botnet'
        db.create_table('hale_botnet', (
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hale.Module'])),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hale', ['Botnet'])

        # Adding model 'Module'
        db.create_table('hale_module', (
            ('confexample', self.gf('django.db.models.fields.TextField')()),
            ('modulename', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('hale', ['Module'])

        # Adding model 'File'
        db.create_table('hale_file', (
            ('analysisurl', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('botnet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hale.Botnet'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('hale', ['File'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Proxy'
        db.delete_table('hale_proxy')

        # Deleting model 'Log'
        db.delete_table('hale_log')

        # Deleting model 'Botnet'
        db.delete_table('hale_botnet')

        # Deleting model 'Module'
        db.delete_table('hale_module')

        # Deleting model 'File'
        db.delete_table('hale_file')
    
    
    models = {
        'hale.botnet': {
            'Meta': {'object_name': 'Botnet'},
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hale.Module']"})
        },
        'hale.file': {
            'Meta': {'object_name': 'File'},
            'analysisurl': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'botnet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hale.Botnet']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
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
            'modulename': ('django.db.models.fields.CharField', [], {'max_length': '32'})
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
