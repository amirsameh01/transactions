from django.urls import path
from notification.views import SendNotificationView

urlpatterns = [
    path('send/', SendNotificationView.as_view(), name='send-notification'),
]
