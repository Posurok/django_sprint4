from django.contrib import admin
from django.urls import include, path

from pages import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        views.RegistrationView.as_view(),
        name='registration'
    ),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.page_500'
