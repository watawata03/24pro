from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('search_app.urls')),  # search_app の urls.py をインクルード
]
