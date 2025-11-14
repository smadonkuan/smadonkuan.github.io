from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from projects.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('projects/', include('projects.urls')),
    path('blog/', include('blog.urls')),
    path('markdownx/', include('markdownx.urls')),  # 新增
]