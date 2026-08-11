from enum import member
import profile
import qrcode
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
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer
from django.http import HttpResponse
from django.urls import reverse

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
            EventMember.objects.filter(event=event).count()
        )

    return render(request, "admin_panel.html", {

        "categories_count": categories_count,
        "events_count": events_count,
        "members_count": members_count,
        "wishlist_count": wishlist_count,
        "completed_events_count": completed_events_count,
        "venue_count": venue_count,
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
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        venue = request.POST.get("venue")
        description = request.POST.get("description")

        Event.objects.create(
            event_name=event_name,
            category=category,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            description=description
        )

        Notification.objects.create(
            title="New Event Created",
            message=f"{event_name} has been created."
        )
        

        return redirect("event_list")

    return render(request, "Create_Event.html", {
        "categories": categories
    })

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

    return render(request, "user_dashboard.html", context)

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

