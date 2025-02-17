"""
URL configuration for the project.

The `urlpatterns` list routes URLs to views. For more information see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt import views as jwt_views
from rest_framework.permissions import AllowAny
from django.conf.urls.static import static
from django.conf import settings
from decouple import config
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_yasg.utils import swagger_auto_schema

# Swagger/OpenAPI schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="MATRIX MOMENTUM",
        default_version="v1.0.0",
        description="Authentication System and Investment Platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
     permission_classes=(AllowAny,),  # Allow access without authentication
)

# Swagger settings based on environment
SWAGGER_ENABLED = config('SWAGGER_ENABLED', default=True, cast=bool)

# URL patterns
urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('account/login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('account/login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('account/', include('account.urls')),

    # App-specific endpoints
    path('api/faq/', include('FAQ.urls')),
    path('api/transaction-history/', include('TransactionHistory.urls')),
    path('api/referral/', include('referral.urls')),
    path('api/contact/', include('CONTACT.urls')),
    path('api/make-deposit/', include('MakeDeposit.urls')),
    path('api/your-deposit/', include('YourDeposit.urls')),
    path('api/referral-links/', include('ReferralLinks.urls')),
    path('api/withdraw/', include('Withdraw.urls')),
    path('api/edit-account/', include('EditAccount.urls')),
    path('api/security/', include('Security.urls')),
    path('api/chat/', include('Chat.urls')),

    # Root redirect to Swagger
    path('', lambda request: HttpResponseRedirect('/api/schema/swagger-ui/'), name='root_redirect'),
]

# Swagger and Redoc - Conditional inclusion for production and development
if SWAGGER_ENABLED:
    urlpatterns += [
        path('internal/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('internal/docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# Static and media files configuration (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += [
    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
