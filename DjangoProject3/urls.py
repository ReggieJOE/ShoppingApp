from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your custom admin routes FIRST (before Django admin)
    path('admin/', include('Commerce.urls')),

    # Django built-in admin (with a different prefix or keep as is)
    path('django-admin/', admin.site.urls),

    # Main site routes
    path('', include('Commerce.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)