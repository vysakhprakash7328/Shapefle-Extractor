# Generated by Django 4.1.7 on 2023-03-28 04:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shapedata', '0064_road'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DRAINAGE_L',
        ),
        migrations.DeleteModel(
            name='FINAL_ROAD_CHIRAKKAL',
        ),
        migrations.DeleteModel(
            name='PANCHAYAT_BOUNDARY',
        ),
        migrations.DeleteModel(
            name='Road',
        ),
    ]