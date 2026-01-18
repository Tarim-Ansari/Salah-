from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # This points the root URL to your accounts app
    path("", include("accounts.urls")), 
    # REMOVED: path('', include('home.urls')), <--- This was causing the crash
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)