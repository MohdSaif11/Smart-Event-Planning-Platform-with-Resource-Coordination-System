from enum import member
import profile
import qrcode
import json
from io import BytesIO
from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Category, Event, EventMember, EventWishList , Notification
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import UserProfile , UserNotification
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.utils import timezone

def create_user_event_notifications(user):
    """
    Create user notifications for events that are
    starting soon or ending soon.
    """

    today = timezone.localdate()

    # ---------------------------------------------------------
    # EVENTS STARTING TODAY OR TOMORROW
    # ---------------------------------------------------------

    starting_events = Event.objects.filter(
        start_date__gte=today,
        start_date__lte=today + timezone.timedelta(days=1)
    )

    for event in starting_events:

        if not UserNotification.objects.filter(
            user=user,
            event=event,
            notification_type="STARTING_SOON"
        ).exists():

            UserNotification.objects.create(
                user=user,
                event=event,
                title="Event Starting Soon",
                message=(
                    f"{event.event_name} is starting "
                    f"on {event.start_date}."
                ),
                notification_type="STARTING_SOON"
            )

    # ---------------------------------------------------------
    # EVENTS ENDING TODAY OR TOMORROW
    # ---------------------------------------------------------

    ending_events = Event.objects.filter(
        end_date__gte=today,
        end_date__lte=today + timezone.timedelta(days=1)
    )

    for event in ending_events:

        if not UserNotification.objects.filter(
            user=user,
            event=event,
            notification_type="ENDING_SOON"
        ).exists():

            UserNotification.objects.create(
                user=user,
                event=event,
                title="Event Ending Soon",
                message=(
                    f"{event.event_name} is ending "
                    f"on {event.end_date}."
                ),
                notification_type="ENDING_SOON"
            )

def get_events_for_ai():
    events = Event.objects.all()

    event_data = []

    for event in events:
        event_data.append({
            "id": event.id,
            "name": event.event_name,
            "category": str(event.category),
            "organizer": event.organizer,
            "start_date": str(event.start_date),
            "end_date": str(event.end_date),
            "venue": event.venue,
            "status": get_event_status(event)
        })

    return event_data

def get_event_status(event):
    today = timezone.localdate()

    if event.end_date < today:
        return "COMPLETED"
    elif event.start_date > today:
        return "UPCOMING"
    else:
        return "ONGOING"
    
@require_POST
def chatbot(request):
    try:
        # =========================================================
        # GET USER MESSAGE
        # =========================================================

        data = json.loads(request.body)
        message = data.get("message", "").strip().lower()

        if not message:
            return JsonResponse({
                "reply": "Please enter a question."
            })

        today = timezone.localdate()

        # =========================================================
        # GET ALL EVENTS
        # =========================================================

        events = Event.objects.all()

        event_data = []

        for event in events:

            if event.end_date < today:
                status = "COMPLETED"

            elif event.start_date > today:
                status = "UPCOMING"

            else:
                status = "ONGOING"

            event_data.append({
                "id": event.id,
                "name": event.event_name,
                "category": event.category,
                "start_date": str(event.start_date),
                "end_date": str(event.end_date),
                "venue": event.venue,
                "description": event.description,
                "status": status
            })

        # =========================================================
        # GET LOGGED-IN USER
        # =========================================================

        user_email = request.user.email

        # =========================================================
        # GET REGISTERED EVENTS
        # =========================================================

        registrations = EventMember.objects.filter(
            email=user_email
        ).select_related("event")

        registered_events = []

        for registration in registrations:

            registered_events.append({
                "event": registration.event.event_name,
                "start_date": str(registration.event.start_date),
                "end_date": str(registration.event.end_date),
                "venue": registration.event.venue,
                "attended": registration.attended
            })

        # =========================================================
        # GET WISHLIST EVENTS
        # =========================================================

        wishlist_items = EventWishList.objects.filter(
            email=user_email
        ).select_related("event")

        wishlist_events = []

        for item in wishlist_items:

            wishlist_events.append({
                "event": item.event.event_name,
                "start_date": str(item.event.start_date),
                "end_date": str(item.event.end_date),
                "venue": item.event.venue
            })

        # =========================================================
        # EVENT COUNTS
        # =========================================================

        total_events = len(event_data)

        ongoing_events = [
            event for event in event_data
            if event["status"] == "ONGOING"
        ]

        upcoming_events = [
            event for event in event_data
            if event["status"] == "UPCOMING"
        ]

        completed_events = [
            event for event in event_data
            if event["status"] == "COMPLETED"
        ]

        active_events = ongoing_events + upcoming_events

        # =========================================================
        # FIND EVENT MENTIONED IN QUESTION
        # =========================================================

        matched_event = None

        for event in event_data:

            event_name = event["name"].lower()
            category = event["category"].lower()

            if (
                event_name in message
                or category in message
            ):
                matched_event = event
                break

        # =========================================================
        # CHATBOT INTENT DETECTION
        # =========================================================

        # =========================================================
        # 1. GREETING
        # =========================================================

        if message in [
            "hi",
            "hello",
            "hey",
            "hi there",
            "hello there",
            "good morning",
            "good afternoon",
            "good evening"
        ]:

            reply = (
                "Hello! 👋 I am your Event Assistant. "
                "I can help you with events, registration, "
                "attendance, wishlist, dates, venues and event status."
            )

        # =========================================================
        # 2. HELP
        # =========================================================

        elif (
            message == "help"
            or "help me" in message
            or "what can you do" in message
            or "what can you help" in message
        ):

            reply = (
                "I can help you with:\n\n"
                "• Finding active events\n"
                "• Upcoming events\n"
                "• Completed events\n"
                "• Event dates and venues\n"
                "• Event details\n"
                "• How to register\n"
                "• Your registered events\n"
                "• Registration count\n"
                "• Attendance\n"
                "• Wishlist\n"
                "• Event categories"
            )

        # =========================================================
        # 3. MY REGISTERED EVENTS - LIST
        # =========================================================

        elif (
            "what events am i registered for" in message
            or "which events am i registered for" in message
            or "what events did i register for" in message
            or "which events did i register for" in message
            or "what have i registered for" in message
            or "which have i registered for" in message
            or "my registered events" in message
            or "my registrations" in message
            or "show my registrations" in message
            or "show my registered events" in message
            or "events i registered for" in message
            or "events i have registered for" in message
            or "events i joined" in message
            or "events i have joined" in message
            or "what did i join" in message
            or "which events did i join" in message
        ):

            if registered_events:

                event_names = ", ".join(
                    event["event"]
                    for event in registered_events
                )

                reply = (
                    f"You are registered for "
                    f"{len(registered_events)} event(s): "
                    f"{event_names}."
                )

            else:

                reply = (
                    "You are not registered for any events."
                )

        # =========================================================
        # 4. REGISTRATION COUNT
        # =========================================================

        elif (
            (
                "how many" in message
                or "how much" in message
                or "number of" in message
                or "count" in message
                or "total" in message
            )
            and (
                "registered" in message
                or "registration" in message
                or "joined" in message
                or "enrolled" in message
            )
        ):

            reply = (
                f"You are registered for "
                f"{len(registered_events)} event(s)."
            )

        # =========================================================
        # 5. CHECK WHETHER USER REGISTERED FOR SPECIFIC EVENT
        # =========================================================

        elif (
            matched_event
            and (
                "am i registered" in message
                or "did i register" in message
                or "have i registered" in message
                or "did i join" in message
                or "have i joined" in message
                or "am i enrolled" in message
            )
        ):

            is_registered = any(
                registration["event"].lower()
                == matched_event["name"].lower()
                for registration in registered_events
            )

            if is_registered:

                reply = (
                    f"Yes. You are registered for "
                    f"{matched_event['name']}."
                )

            else:

                reply = (
                    f"No. You are not registered for "
                    f"{matched_event['name']}."
                )

        # =========================================================
        # 6. HOW TO REGISTER
        # =========================================================

        elif (
            "how do i register" in message
            or "how can i register" in message
            or "how to register" in message
            or "how do i signup" in message
            or "how can i signup" in message
            or "how do i sign up" in message
            or "how can i sign up" in message
            or "how do i join" in message
            or "how can i join" in message
            or "how do i participate" in message
            or "how can i participate" in message
            or "how to participate" in message
            or "registration process" in message
            or "registration procedure" in message
            or "i want to register" in message
            or "i want to join" in message
            or "i want to participate" in message
            or "how can i enroll" in message
            or "how do i enroll" in message
        ):

            if matched_event:

                reply = (
                    f"To register for {matched_event['name']}, "
                    f"open the event and click the Register button. "
                    f"Follow the registration process to join the event."
                )

            else:

                reply = (
                    "To register for an event, go to the Events section, "
                    "select the event you are interested in, and click "
                    "the Register button."
                )

        # =========================================================
        # 7. ATTENDANCE
        # =========================================================

        elif (
            "attendance" in message
            or "attended" in message
            or "did i attend" in message
            or "have i attended" in message
            or "which events did i attend" in message
            or "which events have i attended" in message
            or "events i attended" in message
            or "my attendance" in message
        ):

            if not registered_events:

                reply = (
                    "You have not registered for any events yet."
                )

            else:

                attended_events = [
                    event for event in registered_events
                    if event["attended"]
                ]

                not_attended_events = [
                    event for event in registered_events
                    if not event["attended"]
                ]

                reply = (
                    f"You have attended "
                    f"{len(attended_events)} event(s) "
                    f"out of {len(registered_events)} "
                    f"registered event(s)."
                )

                if attended_events:

                    attended_names = ", ".join(
                        event["event"]
                        for event in attended_events
                    )

                    reply += (
                        f" Attended: {attended_names}."
                    )

                if not_attended_events:

                    not_attended_names = ", ".join(
                        event["event"]
                        for event in not_attended_events
                    )

                    reply += (
                        f" Not attended: {not_attended_names}."
                    )

        # =========================================================
        # 8. ATTENDANCE COUNT
        # =========================================================

        elif (
            (
                "how many" in message
                or "number of" in message
                or "count" in message
            )
            and (
                "attended" in message
                or "attendance" in message
            )
        ):

            attended_count = sum(
                1
                for event in registered_events
                if event["attended"]
            )

            reply = (
                f"You have attended {attended_count} "
                f"out of {len(registered_events)} "
                f"registered event(s)."
            )

        # =========================================================
        # 9. SPECIFIC EVENT ATTENDANCE
        # =========================================================

        elif (
            matched_event
            and (
                "did i attend" in message
                or "have i attended" in message
                or "attended" in message
            )
        ):

            registration = next(
                (
                    event
                    for event in registered_events
                    if event["event"].lower()
                    == matched_event["name"].lower()
                ),
                None
            )

            if registration:

                if registration["attended"]:

                    reply = (
                        f"Yes. You attended "
                        f"{matched_event['name']}."
                    )

                else:

                    reply = (
                        f"You are registered for "
                        f"{matched_event['name']}, "
                        f"but attendance has not been marked yet."
                    )

            else:

                reply = (
                    f"You are not registered for "
                    f"{matched_event['name']}."
                )

        # =========================================================
        # 10. WISHLIST
        # =========================================================

        elif (
            "wishlist" in message
            or "wish list" in message
            or "saved event" in message
            or "saved events" in message
            or "favorite event" in message
            or "favourite event" in message
            or "my favorites" in message
            or "my favourites" in message
        ):

            if wishlist_events:

                event_names = ", ".join(
                    event["event"]
                    for event in wishlist_events
                )

                reply = (
                    f"You have {len(wishlist_events)} event(s) "
                    f"in your wishlist: {event_names}."
                )

            else:

                reply = (
                    "Your wishlist is currently empty."
                )

        # =========================================================
        # 11. WISHLIST COUNT
        # =========================================================

        elif (
            (
                "how many" in message
                or "number of" in message
                or "count" in message
            )
            and (
                "wishlist" in message
                or "wish list" in message
                or "saved events" in message
                or "saved event" in message
            )
        ):

            reply = (
                f"You have {len(wishlist_events)} event(s) "
                f"in your wishlist."
            )

        # =========================================================
        # 12. ACTIVE EVENTS
        # =========================================================

        elif (
            "active" in message
            or "still active" in message
            or "currently available" in message
            or "currently active" in message
            or "available events" in message
            or "events available" in message
        ):

            if active_events:

                event_names = ", ".join(
                    event["name"]
                    for event in active_events
                )

                reply = (
                    f"There are {len(active_events)} active event(s). "
                    f"They are: {event_names}."
                )

            else:

                reply = (
                    "There are currently no active events."
                )

        # =========================================================
        # 13. ONGOING EVENTS
        # =========================================================

        elif (
            "ongoing" in message
            or "happening now" in message
            or "currently happening" in message
            or "happening today" in message
            or "today's events" in message
            or "todays events" in message
            or "events today" in message
            or "what is happening today" in message
        ):

            if ongoing_events:

                event_names = ", ".join(
                    event["name"]
                    for event in ongoing_events
                )

                reply = (
                    f"There are {len(ongoing_events)} "
                    f"ongoing event(s): {event_names}."
                )

            else:

                reply = (
                    "There are no events happening today."
                )

        # =========================================================
        # 14. UPCOMING EVENTS
        # =========================================================

        elif (
            "upcoming" in message
            or "coming events" in message
            or "future events" in message
            or "next events" in message
            or "events coming" in message
            or "events that are coming" in message
        ):

            if upcoming_events:

                event_names = ", ".join(
                    event["name"]
                    for event in upcoming_events
                )

                reply = (
                    f"There are {len(upcoming_events)} "
                    f"upcoming event(s): {event_names}."
                )

            else:

                reply = (
                    "There are no upcoming events."
                )

        # =========================================================
        # 15. COMPLETED EVENTS
        # =========================================================

        elif (
            "completed" in message
            or "finished events" in message
            or "past events" in message
            or "ended events" in message
            or "events that ended" in message
        ):

            if completed_events:

                event_names = ", ".join(
                    event["name"]
                    for event in completed_events
                )

                reply = (
                    f"There are {len(completed_events)} "
                    f"completed event(s): {event_names}."
                )

            else:

                reply = (
                    "There are no completed events."
                )

        # =========================================================
        # 16. TOTAL EVENT COUNT
        # =========================================================

        elif (
            (
                "how many" in message
                or "number of" in message
                or "count" in message
                or "total" in message
            )
            and "event" in message
        ):

            reply = (
                f"There are {total_events} events in total. "
                f"{len(ongoing_events)} are ongoing, "
                f"{len(upcoming_events)} are upcoming, and "
                f"{len(completed_events)} are completed."
            )

        # =========================================================
        # 17. EVENT DATE
        # =========================================================

        elif matched_event and (
            "when" in message
            or "date" in message
            or "start date" in message
            or "end date" in message
            or "starts" in message
            or "ends" in message
            or "when does" in message
        ):

            reply = (
                f"{matched_event['name']} starts on "
                f"{matched_event['start_date']} and ends on "
                f"{matched_event['end_date']}."
            )

        # =========================================================
        # 18. EVENT VENUE
        # =========================================================

        elif matched_event and (
            "where" in message
            or "venue" in message
            or "location" in message
            or "place" in message
        ):

            reply = (
                f"{matched_event['name']} will be held at "
                f"{matched_event['venue']}."
            )

        # =========================================================
        # 19. EVENT CATEGORY
        # =========================================================

        elif matched_event and (
            "category" in message
            or "type" in message
        ):

            reply = (
                f"{matched_event['name']} belongs to the "
                f"{matched_event['category']} category."
            )

        # =========================================================
        # 20. EVENT DETAILS
        # =========================================================

        elif matched_event and (
            "description" in message
            or "about" in message
            or "tell me about" in message
            or "details" in message
            or "information" in message
            or "more about" in message
        ):

            reply = (
                f"Here are the details for "
                f"{matched_event['name']}:\n\n"
                f"Category: {matched_event['category']}\n"
                f"Start Date: {matched_event['start_date']}\n"
                f"End Date: {matched_event['end_date']}\n"
                f"Venue: {matched_event['venue']}\n"
                f"Status: {matched_event['status']}\n"
                f"Description: {matched_event['description']}"
            )

        # =========================================================
        # 21. SPECIFIC EVENT STATUS
        # =========================================================

        elif matched_event and (
            "status" in message
            or "is it ongoing" in message
            or "is it upcoming" in message
            or "is it completed" in message
            or "is it finished" in message
        ):

            reply = (
                f"{matched_event['name']} is currently "
                f"{matched_event['status']}."
            )

        # =========================================================
        # 22. GENERAL EVENT SEARCH
        # =========================================================

        elif matched_event:

            reply = (
                f"{matched_event['name']} is a "
                f"{matched_event['category']} event.\n\n"
                f"Start Date: {matched_event['start_date']}\n"
                f"End Date: {matched_event['end_date']}\n"
                f"Venue: {matched_event['venue']}\n"
                f"Status: {matched_event['status']}\n\n"
                f"{matched_event['description']}"
            )

        # =========================================================
        # 23. UNKNOWN QUESTION
        # =========================================================

        else:

            reply = (
                "I couldn't understand that question yet.\n\n"
                "You can ask me things like:\n"
                "• How many events are active?\n"
                "• How can I register for an event?\n"
                "• How many events have I registered?\n"
                "• What events am I registered for?\n"
                "• Am I registered for Basketball?\n"
                "• Which events have I attended?\n"
                "• What is my attendance?\n"
                "• What is in my wishlist?\n"
                "• Which events are upcoming?\n"
                "• Which events are completed?\n"
                "• Where is the Basketball event?\n"
                "• When does the Basketball event start?\n"
                "• Tell me about Basketball."
            )

        # =========================================================
        # DEBUG INFORMATION
        # =========================================================

        context = {
            "current_date": str(today),
            "events": event_data,
            "registered_events": registered_events,
            "wishlist_events": wishlist_events
        }

        print("CHATBOT QUESTION:", message)
        print("CHATBOT ANSWER:", reply)

        # =========================================================
        # RETURN RESPONSE
        # =========================================================

        return JsonResponse({
            "reply": reply,
            "context": context
        })

    except Exception as e:

        print("CHATBOT ERROR:", str(e))

        return JsonResponse(
            {
                "reply": (
                    "Sorry, something went wrong "
                    "while processing your request."
                )
            },
            status=500
        )
    
def admin_required(user):
    return user.is_staff

def public_event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    return render(request, "public_event_details.html", {
        "event": event
    })

def public_register_event(request, id):

    event = get_object_or_404(Event, id=id)

    today = timezone.localdate()

    if event.end_date < today:
        messages.error(
            request,
            "Registration for this event has been closed."
        )
        return redirect("public_event_details", event_id=id)

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        college = request.POST.get("college", "").strip()

        if not name or not email or not phone or not college:
            messages.error(
                request,
                "Please fill in all the required fields."
            )
            return render(
                request,
                "public_register_event.html",
                {"event": event}
            )

        if not phone.isdigit() or len(phone) != 10:
            messages.error(
                request,
                "Please enter a valid 10-digit phone number."
            )
            return render(
                request,
                "public_register_event.html",
                {"event": event}
            )

        if EventMember.objects.filter(
            email=email,
            event=event
        ).exists():

            messages.warning(
                request,
                "This email is already registered for this event."
            )

            return redirect(
                "public_event_details",
                event_id=id
            )

        member = EventMember.objects.create(
            name=name,
            email=email,
            phone=phone,
            college=college,
            event=event
        )

        qr_data = str(member.id)

        qr = qrcode.make(qr_data)

        buffer = BytesIO()

        qr.save(buffer, format="PNG")

        member.qr_code.save(
            f"qr_{member.id}.png",
            File(buffer),
            save=True
        )

        Notification.objects.create(
            title="New Event Registration",
            message=f"{name} registered for {event.event_name}."
        )

        return render(
            request,
            "public_registration_success.html",
            {
                "member": member,
                "event": event
            }
        )

    return render(
        request,
        "public_register_event.html",
        {"event": event}
    )

@login_required
@user_passes_test(admin_required)
def event_qr(request, event_id):

    event = get_object_or_404(Event, id=event_id)

    event_url = request.build_absolute_uri(
        reverse("public_event_details", args=[event.id])
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(event_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    response = HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )

    response["Content-Disposition"] = (
        f'inline; filename="event_{event.id}_qr.png"'
    )

    return response

@api_view(["GET"])
def api_events(request):

    events = Event.objects.all()

    serializer = EventSerializer(events, many=True)

    return Response(serializer.data)

@api_view(["GET"])
def api_event_details(request, id):

    event = Event.objects.get(id=id)

    serializer = EventSerializer(event)

    return Response(serializer.data)

@require_POST
def mark_notifications_read(request):

    Notification.objects.filter(is_read=False).update(is_read=True)

    return JsonResponse({
        "status": "success"
    })

@login_required
def user_notifications(request):

    # Generate starting/ending reminders
    create_user_event_notifications(request.user)

    notifications = UserNotification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    notification_data = []

    for notification in notifications:

        notification_data.append({
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at.strftime(
                "%d %b %Y, %I:%M %p"
            ),
            "event_id": (
                notification.event.id
                if notification.event
                else None
            )
        })

    unread_count = UserNotification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        "notifications": notification_data,
        "unread_count": unread_count
    })


@login_required
@require_POST
def mark_user_notifications_read(request):

    UserNotification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return JsonResponse({
        "status": "success"
    })


@login_required
def change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")

        if request.user.check_password(new_password):
            messages.error(request,"Your new password cannot be the same as your current password.")
            return redirect("change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, "Password changed successfully.")

        return redirect("settings")

    return render(request, "change_password.html")

def admin_required(user):
    return user.is_staff

def signup(request):
    if request.method == "POST":

        fullname = request.POST.get("fullname")
        phone = request.POST.get("phone")
        college = request.POST.get("college")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        if password != confirm_password:
            return render(request, "signup.html", {
                "error": "Passwords do not match."
            })

        if User.objects.filter(username=email).exists():
            return render(request, "signup.html", {
                "error": "Email already exists."
            })

        user = User.objects.create_user(
            username=email,
            first_name=fullname,
            email=email,
            password=password
        )

        if role == "admin":
            user.is_staff = True
            user.save()

        UserProfile.objects.create(
            user=user,
            phone=phone,
            college=college
        )

        Notification.objects.create(
            title="New User Registered",
            message=f"{fullname} has registered successfully."
        )

        return redirect("login")

    return render(request, "signup.html")

def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff:
                return redirect("admin_panel")

            return redirect("user_dashboard")

        return render(request, "login.html", {
            "error": "Invalid Email or Password"
        })

    return render(request, "login.html")


def home(request):
    return redirect("admin_panel")

@login_required
@user_passes_test(admin_required)
def admin_panel(request):

    categories_count = Category.objects.count()

    events_count = Event.objects.count()

    members_count = EventMember.objects.count()

    wishlist_count = EventWishList.objects.count()

    completed_events_count = Event.objects.filter(
        end_date__lt=timezone.localdate()
    ).count()

    venue_count = Event.objects.values("venue").distinct().count()

    # Count unique organizers
    organizer_count = Event.objects.exclude(
        organizer__isnull=True
    ).exclude(
        organizer=""
    ).values(
        "organizer"
    ).distinct().count()

    events = Event.objects.all().order_by("-id")[:5]

    # ------------------------------
    # Analytics Data for Chart
    # ------------------------------

    event_names = []

    registration_counts = []

    all_events = Event.objects.all()

    for event in all_events:

        event_names.append(event.event_name)

        registration_counts.append(
            EventMember.objects.filter(
                event=event
            ).count()
        )

    return render(request, "admin_panel.html", {

        "categories_count": categories_count,

        "events_count": events_count,

        "members_count": members_count,

        "wishlist_count": wishlist_count,

        "completed_events_count": completed_events_count,

        "venue_count": venue_count,

        "organizer_count": organizer_count,

        "events": events,

        # Analytics
        "event_names": event_names,

        "registration_counts": registration_counts,

    })


@login_required
@user_passes_test(admin_required)
def create_category(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name")
        category_code = request.POST.get("category_code")

        Category.objects.create(
            category_name=category_name,
            category_code=category_code
        )

        return redirect("category_list")

    return render(request, "create_category.html")

@login_required
@user_passes_test(admin_required)
def category_list(request):
    categories = Category.objects.all()

    return render(request, "category_list.html", {
        "categories": categories
    })

@login_required
@user_passes_test(admin_required)
def create_event(request):

    categories = Category.objects.all()

    if request.method == "POST":

        event_name = request.POST.get("event_name")
        category = request.POST.get("category")
        organizer = request.POST.get("organizer")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        venue = request.POST.get("venue")
        description = request.POST.get("description")

        # -----------------------------------------------------
        # CREATE EVENT
        # -----------------------------------------------------

        event = Event.objects.create(
            event_name=event_name,
            category=category,
            organizer=organizer,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            description=description
        )

        # -----------------------------------------------------
        # ADMIN NOTIFICATION
        # -----------------------------------------------------

        Notification.objects.create(
            title="New Event Created",
            message=f"{event_name} has been created."
        )

        # -----------------------------------------------------
        # USER NOTIFICATIONS
        # -----------------------------------------------------

        users = User.objects.filter(
            is_active=True,
            is_staff=False
        )

        for user in users:

            UserNotification.objects.create(
                user=user,
                event=event,
                title="New Event Available",
                message=(
                    f"A new event '{event_name}' "
                    f"is now available."
                ),
                notification_type="NEW_EVENT"
            )

        return redirect("event_list")

    return render(
        request,
        "Create_Event.html",
        {
            "categories": categories
        }
    )

@login_required
@user_passes_test(admin_required)
def event_list(request):
    events = Event.objects.all()

    return render(request, "event_list.html", {
        "events": events
    })

@login_required
@user_passes_test(admin_required)
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        event.event_name = request.POST.get("event_name")
        event.category = request.POST.get("category")
        event.start_date = request.POST.get("start_date")
        event.end_date = request.POST.get("end_date")
        event.venue = request.POST.get("venue")
        event.description = request.POST.get("description")

        event.save()

        return redirect("event_list")

    return render(request, "edit_event.html", {
        "event": event,
        "categories": categories
    })

@login_required
@user_passes_test(admin_required)
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()

    return redirect("event_list")

@login_required
@user_passes_test(admin_required)
def add_event_member(request):

    print("METHOD =", request.method)

    events = Event.objects.all()

    if request.method == "POST":

        print("POST DATA =", request.POST)

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        college = request.POST.get("college")
        event_id = request.POST.get("event")

        print(name, email, phone, college, event_id)

        event = get_object_or_404(Event, id=event_id)

        EventMember.objects.create(
            name=name,
            email=email,
            phone=phone,
            college=college,
            event=event
        )

        print("MEMBER SAVED")

        return redirect("join_event_list")

    return render(request, "add_event_member.html", {
        "events": events
    })

@login_required
@user_passes_test(admin_required)
def join_event_list(request):

    members = EventMember.objects.select_related("event").all()

    return render(request, "join_event_list.html", {
        "members": members
    })


@login_required
@user_passes_test(admin_required)
def edit_event_member(request, id):

    member = get_object_or_404(EventMember, id=id)
    events = Event.objects.all()

    if request.method == "POST":

        member.name = request.POST.get("name")
        member.email = request.POST.get("email")
        member.phone = request.POST.get("phone")
        member.college = request.POST.get("college")
        member.event_id = request.POST.get("event")

        member.save()

        return redirect("join_event_list")

    return render(request, "edit_event_member.html", {
        "member": member,
        "events": events
    })

@login_required
@user_passes_test(admin_required)
def delete_event_member(request, id):
    member = get_object_or_404(EventMember, id=id)
    member.delete()

    return redirect("join_event_list")

@login_required
@user_passes_test(admin_required)
def event_wish_list(request):
    wishes = EventWishList.objects.select_related("event").all()

    return render(request, "event_wish_list.html", {
        "wishes": wishes
    })

@login_required
@user_passes_test(admin_required)
def add_event_wish_user(request):

    events = Event.objects.all()

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        event_id = request.POST.get("event")

        event = get_object_or_404(Event, id=event_id)


        EventWishList.objects.create(
            name=name,
            email=email,
            event=event
        )

        return redirect("event_wish_list")

    return render(request, "add_event_wish_user.html", {
        "events": events
    })

@login_required
@user_passes_test(admin_required)
def delete_event_wish(request, id):
    wish = get_object_or_404(EventWishList, id=id)
    wish.delete()

    return redirect("event_wish_list")

@login_required
@user_passes_test(admin_required)
def complete_event_list(request):
    today = timezone.localdate()

    completed_events = Event.objects.filter(
        end_date__lt=today
    ).order_by("-end_date")

    return render(request, "complete_event_list.html", {
        "completed_events": completed_events
    })


##user

from django.utils import timezone

@login_required
def user_dashboard(request):

    # Create user-specific event reminders
    create_user_event_notifications(request.user)

    today = timezone.localdate()

    events = Event.objects.all().order_by("-id")[:5]

    total_events = Event.objects.count()

    registered_events = EventMember.objects.filter(
        email=request.user.email
    ).count()

    wishlist = EventWishList.objects.filter(
        email=request.user.email
    ).count()

    completed_events = Event.objects.filter(
        end_date__lt=today
    ).count()

    active_events = Event.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).count()

    upcoming_events = Event.objects.filter(
        start_date__gt=today
    ).count()

    context = {

        "total_events": total_events,

        "registered_events": registered_events,

        "wishlist": wishlist,

        "completed_events": completed_events,

        "active_events": active_events,

        "upcoming_events": upcoming_events,

        "events": events
    }

    return render(
        request,
        "user_dashboard.html",
        context
    )

def user_event_list(request):
    events = Event.objects.all().order_by("-id")

    context = {
        "events": events
    }

    return render(request, "user_event_list.html", context)


def event_details(request, id):

    event = Event.objects.get(id=id)

    context = {
        "event": event
    }

    return render(request, "event_details.html", context)

@login_required
def register_event(request, id):

    event = get_object_or_404(Event, id=id)

    profile = get_object_or_404(UserProfile, user=request.user)

    today = timezone.localdate()

    if event.end_date < today:

        messages.error(
            request,
            "Registration for this event has been closed."
        )

        return redirect("event_details", id=id)

    if EventMember.objects.filter(
        email=request.user.email,
        event=event
    ).exists():

        messages.warning(
            request,
            "You have already registered for this event."
        )

        return redirect("my_registrations")

    member = EventMember.objects.create(
        name=request.user.first_name,
        email=request.user.email,
        phone=profile.phone,
        college=profile.college,
        event=event
    )

    qr_data = str(member.id)

    qr = qrcode.make(qr_data)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    member.qr_code.save(
        f"qr_{member.id}.png",
        File(buffer),
        save=True
    )

    Notification.objects.create(
        title="New Event Registration",
        message=f"{request.user.first_name} registered for {event.event_name}."
    )

    UserNotification.objects.create(
        user=request.user,
        event=event,
        title="Registration Successful",
        message=(
            f"You successfully registered for "
            f"{event.event_name}."
        ),
        notification_type="REGISTRATION"
    )

    messages.success(
        request,
        "Event registered successfully."
    )

    return redirect("my_registrations")


@login_required
def my_registrations(request):

    registrations = EventMember.objects.filter(
        email=request.user.email
    ).select_related("event")

    return render(
        request,
        "my_registrations.html",
        {
            "registrations": registrations
        }
    )


@login_required
def wishlist(request):

    wishes = EventWishList.objects.filter(
    email=request.user.email
    ).select_related("event")

    return render(
        request,
        "wishlist.html",
        {
            "wishes": wishes
        }
    )

@login_required
def add_to_wishlist(request, id):

    event = get_object_or_404(Event, id=id)

    if EventWishList.objects.filter(
        email=request.user.email,
        event=event
    ).exists():
        return redirect("wishlist")

    EventWishList.objects.create(
        name=request.user.first_name,
        email=request.user.email,
        event=event
    )

    Notification.objects.create(
        title="Wishlist Updated",
        message=f"{request.user.first_name} added {event.event_name} to wishlist."
    )

    UserNotification.objects.create(
        user=request.user,
        event=event,
        title="Added to Wishlist",
        message=(
            f"{event.event_name} has been added "
            f"to your wishlist."
        ),
        notification_type="WISHLIST"
    )

    return redirect("wishlist")

def completed_events(request):

    events = Event.objects.filter(end_date__lt=date.today()).order_by("-end_date")

    context = {
        "events": events
    }

    return render(request, "completed_events.html", context)


@login_required
def profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)

    context = {
        "user": request.user,
        "profile": profile
    }

    if request.user.is_staff:
        return render(request, "admin_profile.html", context)

    return render(request, "user_profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def settings_view(request):
    return render(request,"settings.html")

@login_required
def settings_view(request):
    return render(request, "settings.html")

@login_required
def edit_profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":

        name = request.POST.get("name").strip()
        phone = request.POST.get("phone").strip()
        college = request.POST.get("college").strip()

        if len(name) < 3:
            messages.error(request, "Name must contain at least 3 characters.")
            return redirect("edit_profile")

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must contain exactly 10 digits.")
            return redirect("edit_profile")

        if len(college) < 3:
            messages.error(request, "Please enter a valid college name.")
            return redirect("edit_profile")

        request.user.first_name = name
        request.user.save()

        profile.phone = phone
        profile.college = college

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        messages.success(request, "Profile updated successfully.")

        return redirect("profile")

    return render(request, "edit_profile.html", {
        "profile": profile
    })

@login_required
def user_change_password(request):

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("user_change_password")

        if new_password != confirm_password:
            messages.error(request, "New password and Confirm password do not match.")
            return redirect("user_change_password")

        if current_password == new_password:
            messages.error(request, "New password cannot be the same as the current password.")
            return redirect("user_change_password")

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect("user_change_password")

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully.")
        return redirect("profile")

    return render(request, "user_change_password.html")

@login_required
def edit_user_profile(request):

    profile = request.user.userprofile

    if request.method == "POST":

        request.user.first_name = request.POST.get("name")
        request.user.email = request.POST.get("email")
        profile.phone = request.POST.get("phone")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        request.user.save()
        profile.save()

        messages.success(request, "Profile updated successfully.")

        return redirect("profile")

    context = {
        "profile": profile
    }

    return render(request, "edit_user_profile.html", context)

@login_required
def scan_qr(request):

    return render(
        request,
        "scan_qr.html"
    )

@login_required
def verify_qr(request, data):

    try:

        member = EventMember.objects.get(id=int(data))

        if member.attended:

            messages.warning(
                request,
                "Attendance already marked."
            )

        else:

            member.attended = True
            member.save()

            messages.success(
                request,
                f"{member.name} attendance marked successfully."
            )

    except EventMember.DoesNotExist:

        messages.error(
            request,
            "Invalid QR Code."
        )

    return redirect("scan_qr")

@login_required
@user_passes_test(admin_required)
def organizer_list(request):

    organizers = Event.objects.exclude(
        organizer__isnull=True
    ).exclude(
        organizer=""
    ).values(
        "organizer"
    ).annotate(
        event_count=Count("id")
    ).order_by(
        "organizer"
    )

    return render(
        request,
        "organizer_list.html",
        {
            "organizers": organizers
        }
    )

