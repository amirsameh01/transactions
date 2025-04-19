from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from notification.models import Notification


class SendNotificationView(APIView):
    
    def post(self, request, *args, **kwargs):
        """
        handle notification creation and asynchronous dispatch.

        creates a notification record in the database and queues it for processing
        via celery workers.
        params:
        - merchantId: ID of associated merchant
        - content: Notification message content
        - mediums: List of communication channels (['sms', 'email'])
        - recipient_info: Destination addresses for each medium(phone number, email, ...)"""

        data = request.data
        required_fields = ["merchantId", "content", "mediums", "recipient_info"]
        
        #NOTE: this is a basic validation since it wasnt the main purpose of the task, otherwise \
                # should have used a serialzier for this in a normal case
        if not all(field in data for field in required_fields):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create notification
        notification = Notification.objects.create(
            merchantId=data["merchantId"],
            content=data["content"],
            mediums=data["mediums"],
            recipient_info=data["recipient_info"],
            status="pending"
        )
        
        from notification.tasks import dispatch_notification
        dispatch_notification.delay(str(notification.id))
        
        return Response(
            {"status": "Notification queued", "notification_id": str(notification.id)},
            status=status.HTTP_202_ACCEPTED
        )