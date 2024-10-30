# urls.py
from django.urls import path
from .views import TransactionHistoryView, RecordTransactionView

urlpatterns = [
    path('transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('transactions/record/', RecordTransactionView.as_view(), name='record-transaction'),
]
