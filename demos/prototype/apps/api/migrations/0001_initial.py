# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'api_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('thumbnail_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['User'])

        # Adding model 'Moment'
        db.create_table(u'api_moment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.User'])),
            ('earliest_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('latest_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'api', ['Moment'])

        # Adding model 'Asset'
        db.create_table(u'api_asset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('date_taken', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_uploaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Asset'])

        # Adding model 'Picture'
        db.create_table(u'api_picture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Asset'])),
            ('moment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Moment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.User'])),
            ('date_uploaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Picture'])

        # Adding model 'Share'
        db.create_table(u'api_share', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shared_by_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='shared_by_user', to=orm['api.User'])),
            ('date_shared', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Share'])

        # Adding M2M table for field shared_with_users on 'Share'
        m2m_table_name = db.shorten_name(u'api_share_shared_with_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('share', models.ForeignKey(orm[u'api.share'], null=False)),
            ('user', models.ForeignKey(orm[u'api.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['share_id', 'user_id'])

        # Adding M2M table for field shared_assets on 'Share'
        m2m_table_name = db.shorten_name(u'api_share_shared_assets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('share', models.ForeignKey(orm[u'api.share'], null=False)),
            ('asset', models.ForeignKey(orm[u'api.asset'], null=False))
        ))
        db.create_unique(m2m_table_name, ['share_id', 'asset_id'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'api_user')

        # Deleting model 'Moment'
        db.delete_table(u'api_moment')

        # Deleting model 'Asset'
        db.delete_table(u'api_asset')

        # Deleting model 'Picture'
        db.delete_table(u'api_picture')

        # Deleting model 'Share'
        db.delete_table(u'api_share')

        # Removing M2M table for field shared_with_users on 'Share'
        db.delete_table(db.shorten_name(u'api_share_shared_with_users'))

        # Removing M2M table for field shared_assets on 'Share'
        db.delete_table(db.shorten_name(u'api_share_shared_assets'))


    models = {
        u'api.asset': {
            'Meta': {'object_name': 'Asset'},
            'date_taken': ('django.db.models.fields.DateTimeField', [], {}),
            'date_uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.User']"})
        },
        u'api.moment': {
            'Meta': {'object_name': 'Moment'},
            'earliest_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_date': ('django.db.models.fields.DateTimeField', [], {}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.User']"})
        },
        u'api.picture': {
            'Meta': {'object_name': 'Picture'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Asset']"}),
            'date_uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Moment']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.User']"})
        },
        u'api.share': {
            'Meta': {'object_name': 'Share'},
            'date_shared': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shared_assets': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['api.Asset']", 'symmetrical': 'False'}),
            'shared_by_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shared_by_user'", 'to': u"orm['api.User']"}),
            'shared_with_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shared_with_user'", 'symmetrical': 'False', 'to': u"orm['api.User']"})
        },
        u'api.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'thumbnail_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        }
    }

    complete_apps = ['api']