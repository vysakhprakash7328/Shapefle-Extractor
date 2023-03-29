import os
from zipfile import ZipFile
from django.http import HttpResponse
from django.shortcuts import redirect, render
import fiona
import geopandas as gpd
from numpy import double, longfloat

from . forms import UploadFileForm, db_connForm
from shapefileectracter import settings

from django.db import models
from django.contrib.gis.db import models


from . models import create_model, linestring_db, polygon_db, shapefile,  upload
from django.contrib.gis.geos import Point,LineString,Polygon

from sridentify import Sridentify

import psycopg2

from django.core.management import call_command
from django.contrib import admin




  


def home(request):

    form = UploadFileForm(request.POST or None , request.FILES or None)
    if request.method == "POST":
        if form.is_valid:
            filedata = upload()  
            filedata.file = request.FILES['file']
            filedata.save()  
        fp = request.FILES['file']
        print(fp)
        with ZipFile(request.FILES['file'],'r') as zipobject:
            zipobject.extractall(path='media/uploads')
        extr_name = str(fp).split(".")
        path = settings.MEDIA_ROOT
        file_list = os.listdir(path + '/uploads')

        f = path+"/uploads/"+extr_name[0]+"/"+extr_name[0]+".shp"
        text = os.path.join(settings.MEDIA_ROOT,'uploads',extr_name[0],extr_name[0]+'.shp')
        data = gpd.read_file(text)
        with fiona.collection(text) as source:
            print(source.schema)
            print(len(source.schema))  
        print(data.geometry[0])
        length = len(data.global_id)

        for i in range(0,length-1):
            mylist = str(data.geometry[i]).split()
            lat = float(str(mylist[1]).replace('(','').replace(')',''))
            lon = float(str(mylist[2]).replace('(','').replace(')',''))
            print(lon)
            print(lat)
            location = Point(lon ,lat ,srid=4326)
            shapefile(gid=data.global_id[i],geom = location).save()
            print(length)
        return render(request,'index.html',{'data':data})



    return render(request,'home.html',{'form':form})


# Create your views here.



def fetchdata(request):
    fp= "D:\Shapefile\CHIRAKKAL\DRAINAGE_L\DRAINAGE_L.shp"
    data = gpd.read_file(fp)
    print(data)
    print(data.geometry[0])
    length = len(data)
    # for i in range(0,length-1):

    mylist = str(data.geometry[0]).split()
    print(mylist[3])
    print(mylist[length])
    print(length)

    lat = float(str(mylist[1]).replace('(','').replace(')',''))
    lon = float(str(mylist[2]).replace('(','').replace(')',''))
    #     print(lon)
    #     print(lat)
        # location = Point(lon ,lat ,srid=4326)
        # shapefile(gid=data.global_id[i],geom = location).save()
    # mylist1 = str(mylist).replace('(','').replace(')','')

    # for i in range(0,length):
    # polygon = ((11.918937891963408 75.35170346786617))', srid=4326)


    # if rslt:
    #     print('success')
    # else:
    #     print('fail')
    return render(request,'index.html',{'data':data})




def proj_file(request):


    ident = Sridentify()
    # from file
    ident.from_file('D:\Shapefile\CHIRAKKAL\PANCHAYAT_BOUNDARY\PANCHAYAT_BOUNDARY.prj')
    rslt = ident.get_epsg()
    print(rslt)
    return render(request,'prj.html')


def linestring_fetch(request):
    form_conn = db_connForm(request.POST or None )
    form = UploadFileForm(request.POST or None , request.FILES or None)
    status = 2
    
    

    if 'btn1' in request.POST:
        if form_conn.is_valid:
            db_name = request.POST['db_name']
            db_user = request.POST['db_user']
            db_pass = request.POST['db_pass']
            db_host = request.POST['db_host']
            db_port = request.POST['db_port']
            try:
                
                settings.DATABASES['default']['NAME'] = db_name
                settings.DATABASES['default']['USER'] = db_user
                settings.DATABASES['default']['PASSWORD'] = db_pass
                settings.DATABASES['default']['HOST'] = db_host
                settings.DATABASES['default']['PORT'] = db_port
                call_command('makemigrations','shapedata')
                call_command('migrate','shapedata','zero', '--fake-initial')
                

                status = 1
                msg = 1
                return render(request,'linestring.html',{'form':form,'status':status,'msg':msg})
            except:
            
                status = 2
                msg = 0
                return render(request,'linestring.html',{'form_conn':form_conn,'status':status,'msg':msg})
    elif 'btn2' in request.POST:
        call_command('makemigrations','shapedata')
        call_command('migrate','shapedata', '--fake-initial')
        

        if form.is_valid:
            filedata = upload()  
            filedata.file = request.FILES['file']
            filedata.save()  

    

        
        fp = request.FILES['file']
        with ZipFile(request.FILES['file'],'r') as zipobject:
            zipobject.extractall(path='media/uploads')
        extr_name = str(fp).split(".")
        path = settings.MEDIA_ROOT
        file_list = os.listdir(path + '/uploads/'+extr_name[0])
        file_name = file_list[0].split('.')

        f = path+"/uploads/"+extr_name[0]+"/"+file_name[0]+".shp"
        file_locshp = os.path.join(settings.MEDIA_ROOT,'uploads',extr_name[0],file_name[0]+'.shp')
        file_locprj = os.path.join(settings.MEDIA_ROOT,'uploads',extr_name[0],file_name[0]+'.prj')

   

        ident = Sridentify()
        ident.from_file(file_locprj)
        srids = ident.get_epsg()

        # fp= "D:\Shapefile\CHIRAKKAL\DRAINAGE_L\DRAINAGE_L.shp"
        data = gpd.read_file(file_locshp)
        columns = list(data.columns.values)
        len_col = len(columns)
        with fiona.collection(file_locshp) as source:
            print(source.schema['properties'][columns[0]])
            field = source.schema['properties'][columns[0]]
            field1 = field.split(':')
            
       

        fields = {}
        for i in range(0,len_col-1):
            field = source.schema['properties'][columns[i]].split(':')
            try:
                if field[0] == 'int':
                    fields.update({columns[i]:models.IntegerField()})
                elif field[0] == 'float':
                    fields.update({columns[i]:models.FloatField()})
                elif field[0] == 'date':
                    fields.update({columns[i]:models.DateField()})
                elif field[0] == 'str':
                    fields.update({columns[i]:models.CharField(max_length=field[1])})
                elif field[0] == 'LineString':
                    fields.update({columns[i]:models.LineStringField()})
                
                
            except:
                fields.update({columns[i]:field[0]})

        if source.schema['geometry'] == 'LineString':
            fields.update({'geom':models.LineStringField()})
        elif source.schema['geometry'] == 'Point':
            fields.update({'geom':models.PointField()})
        elif source.schema['geometry'] == 'Polygon':
            fields.update({'geom':models.PolygonField()})



        

        

        


        MyModel = create_model(str(extr_name[0]), fields)

        MyModel._meta.managed = False




        

        
        call_command('makemigrations','shapedata')
        call_command('migrate','shapedata', '--fake-initial')

        admin.site.register(MyModel)

        length = len(data)
        col = []
        for i in range(0,len_col-1):
            col.append(columns[i] )
            # col1 = col1 + col
        for i in range(0,length):
            
            d = []
            for j in range(0,len_col-1):
                d.append( "'"+ str(data[columns[j]][i]) +"'" )

            
                
                


        
        print(col)
        print(d)

        if source.schema['geometry'] == 'LineString':

            for i in range(0,length):
                mylist = str(data.geometry[i]).split(" ")



                len_row = len(mylist)
                
                mylists = []
                for k in range(1,len_row):
                    mylists.append(mylist[k].replace('(','').replace(')',''))
                s = {}

                

                mylist1=()
                list2 = []
                for k in range(0,len_row-1,2):
                    for j in range(k+1,len_row-1):

                        mylist1 = (longfloat(mylists[k].replace(',','')),longfloat(mylists[j].replace(',','')))
                        list2.append(mylist1)
                        break
                loc = LineString (list2,srid = srids)


                for j in range(0,len_col-1):
                



                    s.update( {col[j]:data[columns[j]][i]})
                s.update({'geom':loc})

                MyModel.objects.create(**s)
    
        elif source.schema['geometry'] == 'Polygon':

            
            mylist = str(data.geometry[0]).split()
    
            mylist = str(data.geometry[0]).split(" ")


            len_row = len(mylist)
            
            mylists = []
            for i in range(1,len_row):
                mylists.append(mylist[i].replace('(','').replace(')',''))


            mylist1=()
            list2 = []
            for i in range(0,len_row-1,2):
                for j in range(i+1,len_row-1):

                    mylist1 = (longfloat(mylists[i].replace(',','')),longfloat(mylists[j].replace(',','')))
                    list2.append(mylist1)
                    break

            s = {}
            loc = Polygon (list2,srid = srids)
            for j in range(0,len_col-1):
                
                s.update( {col[j]:data[columns[j]][0]})
            s.update({'geom':loc})

            MyModel.objects.create(**s)

        if source.schema['geometry'] == 'Point':
            for i in range(0,length-1):
                mylist = str(data.geometry[i]).split()
                lat = float(str(mylist[1]).replace('(','').replace(')',''))
                lon = float(str(mylist[2]).replace('(','').replace(')',''))
               
                location = Point(lon ,lat ,srid=4326)
                s = {}
                for j in range(0,len_col-1):
                    
                    s.update( {col[j]:data[columns[j]][0]})
                s.update({'geom':location})

                MyModel.objects.create(**s)


                call_command('makemigrations','shapedata')
                call_command('migrate','shapedata','zero', '--fake-initial')
        

    

            
            

            
        
            # linestring_db(Rd_ID = "23412",geom = loc).save()

        
            # cr = MyModel(RD_NAME = 'gdfh',geom = loc).save()
            # print(cr)
            # 


        


        
        # dbHost     = settings.DATABASES['default']['HOST']
        # dbUsername = settings.DATABASES['default']['USER']
        # dbPassword = settings.DATABASES['default']['PASSWORD']
        # dbName     = settings.DATABASES['default']['NAME']
        # dbPort     = settings.DATABASES['default']['PORT']
        # conn = psycopg2.connect(
            
        # database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port= dbPort

        # )
        # query = ''
        # cursor = conn.cursor()
        # for i in range(0,len_col-1):
        #     # if columns[i] == 'CHECK':
        #     #     continue
        #     query1 = columns[i] + ' ' + fields[columns[i]]+','
        #     query = query + query1
            
            
            
        # query2 = query.replace('str','varchar')
        # sql ='''CREATE TABLE IF NOT EXISTS ''' + str(extr_name[0]) + ''' ('''+query2+'''geom geometry)'''
       
            
        # cursor.execute(sql)
        # conn.commit()


        

            
            
    
        # length = len(data)
        # for i in range(0,length):
        #     mylist = str(data.geometry[i]).split(" ")



        #     len_row = len(mylist)
            
        #     mylists = []
        #     for i in range(1,len_row):
        #         mylists.append(mylist[i].replace('(','').replace(')',''))

        
        #     mylist1=()
        #     list2 = []
        #     for i in range(0,len_row-1,2):
        #         for j in range(i+1,len_row-1):

        #             mylist1 = (longfloat(mylists[i].replace(',','')),longfloat(mylists[j].replace(',','')))
        #             list2.append(mylist1)
        #             break


            
        #     loc = LineString (list2,srid = srids)
        
        #     # linestring_db(Rd_ID = "23412",geom = loc).save()
         
        


        
        # conn = psycopg2.connect(
        
        # database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port= dbPort

        # )

        # col1 = ''
        # cursor = conn.cursor()
        # for i in range(0,len_col-1):
        #     col = columns[i] + ','
        #     col1 = col1 + col
        # for i in range(0,length):
        #     d1 = ''
        #     for j in range(0,len_col-1):
        #         d = "'"+ str(data[columns[j]][i]) +"'" + ','
        #         d1 = d1 + d

        # print(col1)
        # print(d1)
            # ins_query = '''INSERT INTO '''+ str(extr_name[0])+'''('''+col1+'''geom)values ('''+ d1+'''ST_SetSRID(ST_GeomFromText(' '''+str(data.geometry[i])+''' '),'''+str(srids)+'''))'''
            # cursor.execute(ins_query)         

        # conn.commit()
        # conn.close()



        status = 1
        msgs = "Table "+ str(extr_name[0]) +" Created successfully"
        tbl_name = str(extr_name[0])
        return render(request,'linestring.html',{'status':status,'msgs':msgs,'form':form})
    
    else:
        return render(request,'linestring.html',{'form':form,'form_conn':form_conn,'status':status})


        


def polygon_fetch(request):

    form = UploadFileForm(request.POST or None , request.FILES or None)
    if request.method == "POST":
        if form.is_valid:
            filedata = upload()  
            filedata.file = request.FILES['file']
            filedata.save()  
        fp = request.FILES['file']
        print(fp)
        with ZipFile(request.FILES['file'],'r') as zipobject:
            zipobject.extractall(path='media/uploads')
        extr_name = str(fp).split(".")
        path = settings.MEDIA_ROOT
        file_list = os.listdir(path + '/uploads')

        f = path+"/uploads/"+extr_name[0]+"/"+extr_name[0]+".shp"
        file_locshp = os.path.join(settings.MEDIA_ROOT,'uploads',extr_name[0],extr_name[0]+'.shp')
        file_locprj = os.path.join(settings.MEDIA_ROOT,'uploads',extr_name[0],extr_name[0]+'.prj')
        
    
        # fp= "D:\Shapefile\CHIRAKKAL\PANCHAYAT_BOUNDARY\PANCHAYAT_BOUNDARY.shp"
        data = gpd.read_file(file_locshp)
        # columns = list(data.columns.values)

        with fiona.collection(file_locshp) as source:
            print(source.schema)
            print(len(source.schema))     
       
        length = len(data)

        ident = Sridentify()
        ident.from_file(file_locprj)
        srids = ident.get_epsg()
        # for i in range(0,length-1):

        mylist = str(data.geometry[0]).split()
  
        mylist = str(data.geometry[0]).split(" ")
        print(data['geometry'])


        len_row = len(mylist)
        
        mylists = []
        for i in range(1,len_row):
            mylists.append(mylist[i].replace('(','').replace(')',''))


        mylist1=()
        list2 = []
        for i in range(0,len_row-1,2):
            for j in range(i+1,len_row-1):

                mylist1 = (longfloat(mylists[i].replace(',','')),longfloat(mylists[j].replace(',','')))
                list2.append(mylist1)
                break


        loc = Polygon (list2,srid = srids)
        polygon_db(objid = "23412",geom = loc).save()
        return HttpResponse("successfull")

    return render(request,'polygon.html',{'form':form})



  
def create_tables(request):
    dbHost     = settings.DATABASES['default']['HOST']
    dbUsername = settings.DATABASES['default']['USER']
    dbPassword = settings.DATABASES['default']['PASSWORD']
    dbName     = settings.DATABASES['default']['NAME']
    dbPort     = settings.DATABASES['default']['PORT']
    conn = psycopg2.connect(
        
    database=dbName, user=dbUsername, password=dbPassword, host=dbHost, port= dbPort

    )
    cursor = conn.cursor()


    sql ='''CREATE TABLE IF NOT EXISTS person(
    FIRST_NAME CHAR(20) NOT NULL,
    LAST_NAME CHAR(20),
    AGE INT
    )'''
    cursor.execute(sql)
    conn.commit()



    # sql1 = "insert into person (FIRST_NAME) values ('Vysakh')"
    # cursor.execute(sql1)
    # conn.commit()
    sql2 = "insert into person (LAST_NAME) values ('prakash')"
    cursor.execute(sql2)
    conn.commit()
    conn.close()







    return HttpResponse("Table created successfully")



def dynamicdb(request):
    # from django.db import connections

    # default_db = connections['default']

    # new_db = default_db.copy()
    # new_db.settings_dict['NAME'] = 'shapedb'

    # cursor = new_db.cursor()
    # cursor.execute('CREATE DATABASE Ults;')
    current_database_name = settings.DATABASES['default']['NAME']

    # set the new database name
    new_database_name = 'shape'
    settings.DATABASES['default']['NAME'] = new_database_name

    call_command('makemigrations')
    call_command('migrate')

    # retrieve data from the new database
    # data = MyModel.objects.all()

    # reset the database name back to the original value
    # settings.DATABASES['default']['NAME'] = current_database_name

    # return render(request, 'my_template.html')
    return HttpResponse("Db created successfully")



# https://pganalyze.com/blog/postgresql-views-django-python