# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-27 18:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_display_name', models.CharField(blank=True, default='', max_length=40, null=True)),
                ('db_email', models.CharField(db_index=True, max_length=254, unique=True)),
                ('db_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_message_id', models.CharField(db_index=True, max_length=254)),
                ('db_date_created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='date created')),
                ('db_text', models.TextField()),
                ('db_html', models.TextField()),
                ('db_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailgun.EmailAddress')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmailThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_subject', models.CharField(default='', max_length=254)),
                ('db_read', models.BooleanField(default=False)),
                ('db_participants', models.ManyToManyField(to='mailgun.EmailAddress')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='emailmessage',
            name='db_thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailgun.EmailThread'),
        ),
    ]
