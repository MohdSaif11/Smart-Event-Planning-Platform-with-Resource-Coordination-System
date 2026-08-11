from .models import Notification

def notification_data(request):

    if request.user.is_authenticated:

        notifications = Notification.objects.order_by("-created_at")[:5]

        unread_count = Notification.objects.filter(is_read=False).count()

        return {
            "notifications": notifications,
            "unread_count": unread_count
        }

    return {}