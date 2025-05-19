from celery import shared_task
from notification.models import Notification
from notification.dispatcher import MEDIUM_HANDLERS, NotificationDispatcher

#TODO: implement some basic logs + transaction black (?)
@shared_task(bind=True, max_retries=3)
def dispatch_notification(self, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        NotificationDispatcher.send(notification)
        notification.update(status="sent")
    except Exception as e:
        notification.update(status="failed")
        self.retry(exc=e, countdown=30) 