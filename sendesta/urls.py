from django.contrib import admin
from django.urls import path , include
from bankapp.views import stripe_webhook
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bankapp.urls')),
    path('accounts/', include('users.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("stripe_webhook", stripe_webhook),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)