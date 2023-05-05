from django.conf import settings
from django.urls import path
from django.conf.urls.static import static


from . import views

urlpatterns = [
    path('home',views.home,name ='home'),
    path('fetchdata', views.fetchdata,name='fetchdata'),
    path('projfile', views.proj_file,name='projfile'),
    path('fetch', views.linestring_fetch,name='linestring_fetch'),
    path('polygon_fetch', views.polygon_fetch,name='polygon_fetch'),
    path('create_tables', views.create_tables,name='create_tables'),
    path('dynamicdb', views.dynamicdb,name='dynamicdb'),
    path('', views.figma,name='figma'),
    
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)