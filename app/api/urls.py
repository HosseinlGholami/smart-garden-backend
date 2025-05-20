from django.urls import path, include
 
urlpatterns = [
    path('garden/', include('garden.urls')),
] 