# Generated by Django 3.2.7 on 2021-09-28 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20210927_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]