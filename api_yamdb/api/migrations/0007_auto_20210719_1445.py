# Generated by Django 2.2.9 on 2021-07-19 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20210718_1415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='titles',
            options={'ordering': ('name',), 'verbose_name': 'Произведение', 'verbose_name_plural': 'Произведения'},
        ),
    ]
