# Generated by Django 3.1.6 on 2021-02-19 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20210216_1647'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Browse',
        ),
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
