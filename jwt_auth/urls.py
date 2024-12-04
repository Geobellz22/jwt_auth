"""
URL configuration for jwt_auth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from account import views

from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt import views as jwt_views

from django.conf.urls.static import static
from django.conf import settings
from account.views import CustomTokenObtainPairView

# Schema View Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="MATRIX MOMENTUM",
        default_version="v1.0.0",
        description="Authentication System",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# URL Patterns
urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('account/login/', CustomTokenObtainPairView.as_view(), name='account_token_obtain_pair'),
    path('account/login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('account/register/', views.register_user, name="sign_up"),
    path('account/confirm/', views.confirm_email, name='confirm_email'),

    # Swagger and Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # App-specific Endpoints
    path('FAQ/API/', include('FAQ.urls')),
    path('transaction-history/API/', include('TransactionHistory.urls')),
    path('referral/', include('referral.urls')),
    path('contact-us/API/', include('CONTACT.urls')),
    path('make-deposit/', include('MakeDeposit.urls')),
    path('your-deposit/', include('YourDeposit.urls')),
    path('referral-link/', include('ReferralLinks.urls')),
    path('withdraw/', include('Withdraw.urls')),
    path('EditAccount/', include('EditAccount.urls')),
    path('security/', include('Security.urls')),
    path('Chat/', include('Chat.urls')),

    # Root Redirect
    path('', lambda request: HttpResponseRedirect('/swagger/'), name='root_redirect'),
]

# Static and Media Files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
