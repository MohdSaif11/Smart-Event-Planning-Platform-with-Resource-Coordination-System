from django.contrib import admin
from .models import Category, Event, EventMember, EventWishList

admin.site.register(Category)
admin.site.register(Event)
admin.site.register(EventMember)
admin.site.register(EventWishList)
