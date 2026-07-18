from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import home


urlpatterns = [
    path("", home, name="home"),

    path("admin/", admin.site.urls),

    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    path(
        "api/resumes/",
        include("resumes.urls"),
    ),

    path(
        "api/ai/",
        include("ai_services.urls"),
    ),
]