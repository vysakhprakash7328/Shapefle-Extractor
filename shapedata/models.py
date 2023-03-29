from django.db import models
from django.contrib.gis.db import models


class shapefile(models.Model):
    gid = models.CharField(max_length=250)
    geom = models.PointField()

class linestring_db(models.Model):
    Rd_ID = models.CharField(max_length=250)
    geom = models.LineStringField()

class polygon_db(models.Model):
    objid = models.CharField(max_length=250)
    geom = models.PolygonField()


class upload(models.Model):
   
    file = models.FileField(upload_to ='uploads/',null=True,blank=True)

class db_connection(models.Model):
    db_name = models.CharField(max_length=250,null=True,blank=True)
    db_user = models.CharField(max_length=250,null=True,blank=True)
    db_pass = models.CharField(max_length=250,null=True,blank=True)
    db_host = models.CharField(max_length=250,null=True,blank=True)
    db_port = models.IntegerField(null=True,blank=True)   


def create_model(name, fields=None, app_label='shapedata'):
    
    class Meta:
        app_label = 'shapedata'
        db_table = name.lower()

    # create a dictionary of field names and types
    attrs = {'__module__': '', 'Meta': Meta}

    # add the fields to the dictionary
    for field_name, field_type in fields.items():
        attrs[field_name] = field_type

    # create the model class
    return type(name, (models.Model,), attrs)
