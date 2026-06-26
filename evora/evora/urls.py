from django.contrib import admin
from django.urls import path, include  # Make sure 'include' is added here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_admin.urls')),  # This hooks up your my_admin routes!
]