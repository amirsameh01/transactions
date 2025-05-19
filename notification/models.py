from mongoengine import Document, IntField, DateTimeField, \
    ObjectIdField, StringField, ListField, ReferenceField, DictField
from django.utils import timezone

class Notification(Document):
    merchantId = ObjectIdField()
    content = StringField()
    mediums = ListField(StringField())
    recipient_info = DictField() # could be encrypted
    status = StringField(choices=["pending", "sent", "failed"])
    retries = IntField(default=0)
    created_at = DateTimeField(default=timezone.now)
    

    meta = {'collection' : 'notification'}


class NotificationLog(Document):
    notification_id = ReferenceField(Notification)
    medium = StringField()
    status = StringField()
    timestamp = DateTimeField()
    error = StringField()

    mate = {'collection' : 'notification_log'}