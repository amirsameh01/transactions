from notification.mediums.handlers import SMSHandler, EmailHandler, TelegramHandler 
from notification.templates import MessageTemplate
from notification.models import Notification, NotificationLog


MEDIUM_HANDLERS = {
    "sms": SMSHandler(),
    "email": EmailHandler(),
    "telegram": TelegramHandler(),
}

class NotificationDispatcher:
    @staticmethod
    def send(notification):
        """ send notification to specified mediums using recipient_info from the notification model """
        for medium in notification.mediums:
            handler = MEDIUM_HANDLERS.get(medium)
            if not handler:
                print(f"Medium {medium} not supported. Skipping.")
                continue

            recipient = notification.recipient_info.get(medium)
            if not recipient:
                print(f"No recipient provided for {medium}. Skipping.")
                continue

            formatted_message = MessageTemplate.format_for_medium(
                notification.content, 
                medium
            )

            try:
                handler.send(formatted_message, recipient)
                NotificationLog.objects.create(
                    notification_id=notification,
                    medium=medium,
                    status="sent"
                )
            except Exception as e:
                NotificationLog.objects.create(
                    notification_id=notification,
                    medium=medium,
                    status="failed",
                    error=str(e)
                )