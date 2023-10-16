from django.urls import include, path
from .views import (SlotBooking, CancelBooking, AddOperator)

urlpatterns = [
    path('slot_booking', SlotBooking.as_view(), name="slot-booking"),
    path('cancel_booking/<str:booking_id>', CancelBooking.as_view(), name="cancel_booking"),
    path('operator/add', AddOperator.as_view(), name="add-operator"),
]