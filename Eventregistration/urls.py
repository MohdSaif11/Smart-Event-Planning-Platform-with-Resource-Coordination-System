from django.contrib import admin
from django.urls import path
from event import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Django Admin
    path("admin/", admin.site.urls),

    # Authentication
    path("", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Admin Dashboard
    path("dashboard/", views.admin_panel, name="home"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),

    # Category
    path("create-category/", views.create_category, name="create_category"),
    path("category-list/", views.category_list, name="category_list"),

    # Event
    path("create-event/", views.create_event, name="create_event"),
    path("event-list/", views.event_list, name="event_list"),
    path("edit-event/<int:id>/", views.edit_event, name="edit_event"),
    path("delete-event/<int:id>/", views.delete_event, name="delete_event"),

    # Event Members
    path("add-event-member/", views.add_event_member, name="add_event_member"),
    path("join-event-list/", views.join_event_list, name="join_event_list"),
    path(
        "edit-event-member/<int:id>/",
        views.edit_event_member,
        name="edit_event_member"
    ),
    path(
        "delete-event-member/<int:id>/",
        views.delete_event_member,
        name="delete_event_member"
    ),

    # Admin Wishlist
    path(
        "event-wish-list/",
        views.event_wish_list,
        name="event_wish_list"
    ),
    path(
        "add-event-wish-user/",
        views.add_event_wish_user,
        name="add_event_wish_user"
    ),
    path(
        "delete-event-wish/<int:id>/",
        views.delete_event_wish,
        name="delete_event_wish"
    ),

    # Completed Events (Admin)
    path(
        "complete-event-list/",
        views.complete_event_list,
        name="complete_event_list"
    ),

    # ==========================
    # User Panel
    # ==========================

    path("user-dashboard/", views.user_dashboard, name="user_dashboard"),
    path("user-events/", views.user_event_list, name="user_event_list"),
    path("event-details/<int:id>/", views.event_details, name="event_details"),
    path("register-event/<int:id>/", views.register_event, name="register_event"),
    path("my-registrations/", views.my_registrations, name="my_registrations"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add-to-wishlist/<int:id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("completed-events/", views.completed_events, name="completed_events"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/", views.settings_view, name="settings"),
    path("change-password/", views.change_password, name="change_password"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path(
    "mark-notifications-read/",
    views.mark_notifications_read,
    name="mark_notifications_read"
),
path(
    "user-change-password/",
    views.user_change_password,
    name="user_change_password",
),
path(
    "edit-user-profile/",
    views.edit_user_profile,
    name="edit_user_profile",
),

path(
    "scan-qr/",
    views.scan_qr,
    name="scan_qr"
),

path(
    "verify-qr/<path:data>/",
    views.verify_qr,
    name="verify_qr"
),
path("api/events/", views.api_events),

path("api/events/<int:id>/", views.api_event_details),

path(
    "event-qr/<int:event_id>/",
    views.event_qr,
    name="event_qr"
),

path(
    "public-event/<int:event_id>/",
    views.public_event_details,
    name="public_event_details"
),
path(
    "public-register/<int:id>/",
    views.public_register_event,
    name="public_register_event"
),

path("chatbot/", views.chatbot, name="chatbot"),

path(
    "user-notifications/",
    views.user_notifications,
    name="user_notifications"
),

path(
    "mark-user-notifications-read/",
    views.mark_user_notifications_read,
    name="mark_user_notifications_read"
),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

