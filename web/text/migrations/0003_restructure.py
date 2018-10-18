# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-12 16:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('text', '0002_thread_db_read'),
    ]

    operations = [
        migrations.CreateModel(
            name='Number',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_phone_number', models.CharField(db_index=True, max_length=7)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='text',
            name='db_recipients',
        ),
        migrations.AlterField(
            model_name='text',
            name='db_sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='text.Number'),
        ),
        migrations.RemoveField(
            model_name='thread',
            name='db_read',
        ),
        migrations.AddField(
            model_name='text',
            name='db_deleted',
            field=models.ManyToManyField(related_name='_text_db_deleted_+', to='text.Number'),
        ),
        migrations.AddField(
            model_name='thread',
            name='db_recipients',
            field=models.ManyToManyField(to='text.Number'),
        ),
        migrations.AddField(
            model_name='thread',
            name='db_read',
            field=models.ManyToManyField(related_name='_thread_db_read_+', to='text.Number'),
        ),
    ]