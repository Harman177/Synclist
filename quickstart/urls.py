from django.urls import path
from . import views
 
app_name = 'quickstart'
 
urlpatterns = [
     path('start/', views.start_session, name='start'),
     path('dashboard/', views.dashboard, name='dashboard'),
 ]