from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')), # Root URL goes to accounts (login/dashboard)
    path('accounts/', include('allauth.urls')),
    path('skills/', include('skills.urls')),
    path('barter/', include('barter.urls')),
    path('reviews/', include('reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
