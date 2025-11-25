"""
URL configuration for testpro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from sound_recorders import current_affairs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('home/', include('home.urls')),
    path('information/', include('information.urls')),# Login as default page
    path('search/', include(('information.search.urls', 'search'), namespace='search')),
    path('change-password/', include(('change_password.urls', 'changepassword'), namespace='changepassword')),
    path('inf_manager/', include('information.inf_manager.urls')),

    path('information/setting/' , include('information.setting.urls')),
    path('sound_recorders/', include('sound_recorders.urls')),
    path('sound_recorders/current_affairs/', include('sound_recorders.current_affairs.urls')),
    path('sound_recorders/current_affairs/create_new/', include('sound_recorders.current_affairs.create_new.urls')),

    path('sound_recorders/report/', include('sound_recorders.report.urls')),
]
