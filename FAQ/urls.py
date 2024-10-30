from django.urls import path
from .views import FAQListCreateView, FAQRetrieveUpdateDestroyView

urlpatterns = [
    path('faq/', FAQListCreateView.as_view(), name='faq-list-create'),
    path('faq/<int:pk>/', FAQRetrieveUpdateDestroyView.as_view(), name='faq-detail'),
]
