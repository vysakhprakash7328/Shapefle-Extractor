# Generated by Django 4.1.7 on 2023-03-27 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shapedata', '0002_drainage_l_delete_road'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DRAINAGE_L',
        ),
    ]