# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-24 10:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0009_remove_contest_min_votes_must_gotten'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contender',
            name='howmany_voted',
            field=models.IntegerField(default=1, verbose_name='Number of photos that is voted by the contender'),
        ),
    ]
