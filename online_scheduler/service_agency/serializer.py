import re

from rest_framework import serializers
from datetime import datetime


def is_valid_phone(obj):
    if not re.search(r"^\+91[\d]{10}$", obj):
        raise serializers.ValidationError("Enter a valid phone number")


class BookingDataSerializer(serializers.Serializer):
    operator_id = serializers.CharField(max_length=225, required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    booking_date = serializers.DateField(required=True)
        
class RescheduleSerializer(serializers.Serializer):
    booking_id = serializers.CharField(max_length=225, required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    booking_date = serializers.DateField(required=True)

class ViewBookingSerializer(serializers.Serializer):
    operator_id = serializers.CharField(max_length=225, required=True)
    booking_date = serializers.DateField(required=False)
    view_booked_slots = serializers.BooleanField(required=True)

class OperatorSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=225, required=True)