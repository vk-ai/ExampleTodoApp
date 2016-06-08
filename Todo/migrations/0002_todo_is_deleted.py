# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Todo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
