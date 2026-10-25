from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "ExpiryBox admin"
admin.site.site_title = "ExpiryBox"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("items.urls")),
    path("", include("notifications.urls")),
    path("", include("impact.urls")),
]

# While developing (DEBUG = True), let Django serve the uploaded photos.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
