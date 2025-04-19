from django.urls import path
from transactions_management.views import TransactionReportView, TransactionSummaryReportView

urlpatterns = [
    path('report/', TransactionReportView.as_view(), name='transactions-report'),
    path('summary-report/', TransactionSummaryReportView.as_view(), name='transactions-summary-report')
]
