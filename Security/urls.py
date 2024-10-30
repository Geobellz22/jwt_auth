from django.urls import path
from .views import SecuritySettingsView, LoginView

urlpatterns = [
    path('settings/', SecuritySettingsView.as_view(), name='security-settings'),
    path('login/', LoginView.as_view(), name='login'),
]
