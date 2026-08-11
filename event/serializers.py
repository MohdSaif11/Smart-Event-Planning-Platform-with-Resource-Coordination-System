from rest_framework import serializers
from .models import Event, EventMember

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMember
        fields = "__all__"
