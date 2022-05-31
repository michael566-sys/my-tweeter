"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path
from rest_framework import routers
from accounts.api.views import UserViewSet, AccountViewSet
from accounts.api import views

router = routers.DefaultRouter()
# general idea: 把api/users 引导到ViewSet的文件里面去
router.register(r'api/users', UserViewSet)
router.register(r'api/accounts', AccountViewSet, basename='accounts')
# base name same as 根目录名字

urlpatterns = [
    path('admin/', admin.site.urls),
    #这个负责首页的显示
    path('', include(router.urls)),
    # this line is copied from:
    # https://www.django-rest-framework.org/tutorial/quickstart/#:~:text=path(%27api%2Dauth/%27%2C%20include(%27rest_framework.urls%27%2C%20namespace%3D%27rest_framework%27))
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
