from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.urls import include


admin.site.site_header = 'E-commerce Admin'
admin.site.site_title = 'E-commerce Admin Portal'
admin.site.index_title = 'Welcome to E-commerce Admin Portal'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('shop.urls')),
]



if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Serve static and media files from development server
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
