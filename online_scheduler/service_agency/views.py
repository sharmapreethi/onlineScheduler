
import uuid
from datetime import datetime
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import BookingDataSerializer, RescheduleSerializer, ViewBookingSerializer, OperatorSerializer
from .models import Booking, Operator

ALL_SLOTS = [
    "00:00:00-01:00:00",
    "01:00:00-02:00:00",
    "02:00:00-03:00:00",
    "03:00:00-04:00:00",
    "04:00:00-05:00:00",
    "05:00:00-06:00:00",
    "06:00:00-07:00:00",
    "07:00:00-08:00:00",
    "08:00:00-09:00:00",
    "09:00:00-10:00:00",
    "10:00:00-11:00:00",
    "11:00:00-12:00:00",
    "12:00:00-13:00:00",
    "13:00:00-14:00:00",
    "14:00:00-15:00:00",
    "15:00:00-16:00:00",
    "16:00:00-17:00:00",
    "17:00:00-18:00:00",
    "18:00:00-19:00:00",
    "19:00:00-20:00:00",
    "20:00:00-21:00:00",
    "21:00:00-22:00:00",
    "22:00:00-23:00:00",
    "23:00:00-00:00:00",
]


class SlotBooking(APIView):
    @extend_schema(
        request=BookingDataSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            412: OpenApiTypes.OBJECT,
            422: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "SUCCESS",
                description="Booking succesfully created",
                value={
                    "sCode": 200,
                    "message": "Booking succesfully created",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={"sCode": 400, "message": "Booking already exists, please slelect some other slot or date"},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 404,
                    "message": "Operator not registered",
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 412,
                    "message": "Start time must be earlier than end time",
                },
                response_only=True,
                status_codes=["412"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 422,
                    "message": "Booking should be for max 1 hour",
                },
                response_only=True,
                status_codes=["422"],
            ),
        ],
    )
    def post(self, request):
        serializer = BookingDataSerializer(data=request.data)
        if not serializer.is_valid():
            serializer_error = serializer.errors
            raise ValidationError(serializer_error)
        data = serializer.validated_data
        operator_id = data["operator_id"]
        booking_date = data["booking_date"]
        booking_start_time = data["start_time"]
        booking_end_time = data["end_time"]

        #check if operator exits

        operator_info = Operator.objects.filter(id=operator_id)

        if not operator_info:
            return Response(
            {"sCode": 404, "message": "Operator not registered",},
            status=status.HTTP_404_NOT_FOUND,
        )

        t1 = datetime.strptime(str(booking_start_time), "%H:%M:%S")
        print('Start time:', t1.time())

        t2 = datetime.strptime(str(booking_end_time), "%H:%M:%S")
        print('End time:', t2.time(), type(booking_end_time))
        
        # to check if start time should be end time
        if t1 > t2:
           if not (str(t1.time()) == "23:00:00" and str(t2.time()) == "00:00:00"):
            return Response(
                {"sCode": 412, "message": "Start time must be earlier than end time",},
                status=status.HTTP_412_PRECONDITION_FAILED,
                )
        
        # get difference
        delta = t2 - t1

        sec = delta.total_seconds()
        print('difference in seconds:', sec)

        min = sec / 60
        print('difference in minutes:', min)

        if str(t1.time()) == "23:00:00" and str(t2.time()) == "00:00:00":
            min = 60

        # to check if the slot that is being booked is for 1 hour
        if min != 60:
            return Response(
            {"sCode": 422, "message": "Booking should be for max 1 hour",},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        #check if operator has any booking for that date and time slot 

        booking_info = Booking.objects.filter(operator_id=operator_id, booking_date=booking_date, start_time=booking_start_time, end_time = booking_end_time)

        if booking_info:
            return Response(
            {"sCode": 400, "message": "Booking already exists, please slelect some other slot or date",},
            status=status.HTTP_400_BAD_REQUEST,
            )
        
        booking_id = str(uuid.uuid4().int)
        booking_id = booking_id[:24]

        params = {
            "booking_id": booking_id,
            "operator_id" : operator_id,
            "booking_date": booking_date,
            "start_time": booking_start_time,
            "end_time": booking_end_time,
            "status": "booked"
        }

        # add booking to DB
        Booking.objects.create(**params)

        return Response(
            {"sCode": 200, "message": "Booking succesfully created", "booking_id": booking_id},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=RescheduleSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            412: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "SUCCESS",
                description="Booking succesfully created",
                value={
                    "sCode": 200,
                    "message": "booking succesfully created",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={"sCode": 400, "message": "Please select some other slot or date"},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 404,
                    "message": "Booking doesnot exists",
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 412,
                    "message": "Start time must be earlier than end time",
                },
                response_only=True,
                status_codes=["412"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 422,
                    "message": "Booking should be for max 1 hour",
                },
                response_only=True,
                status_codes=["422"],
            ),
            
        ],
    )
    def patch(self, request):
        # to reschedule booking
        serializer = RescheduleSerializer(data=request.data)
        if not serializer.is_valid():
            serializer_error = serializer.errors
            raise ValidationError(serializer_error)
        data = serializer.validated_data
        booking_id = data["booking_id"]
        booking_date = data["booking_date"]
        booking_start_time = data["start_time"]
        booking_end_time = data["end_time"]

        #check if booking exists

        booking_info = Booking.objects.filter(booking_id=booking_id)

        if not booking_info:
            return Response(
            {"sCode": 404, "message": "Booking doesnot exists",},
            status=status.HTTP_404_NOT_FOUND,
        )

        booking_info = booking_info.exclude(status="cancelled")

        if not booking_info:
            return Response(
            {"sCode": 404, "message": "Booking doesnot exists",},
            status=status.HTTP_404_NOT_FOUND,
        )

        t1 = datetime.strptime(str(booking_start_time), "%H:%M:%S")
        print('Start time:', t1.time())

        t2 = datetime.strptime(str(booking_end_time), "%H:%M:%S")
        print('End time:', t2.time(), type(booking_end_time))

        # check if start time is before end time 
        if t1 > t2:
           if not (str(t1.time()) == "23:00:00" and str(t2.time()) == "00:00:00"):
            return Response(
                {"sCode": 412, "message": "Start time must be earlier than end time",},
                status=status.HTTP_412_PRECONDITION_FAILED,
                ) 
        
        # get difference
        delta = t2 - t1

        sec = delta.total_seconds()
        print('difference in seconds:', sec)

        min = sec / 60
        print('difference in minutes:', min)

        if str(t1.time()) == "23:00:00" and str(t2.time()) == "00:00:00":
            min = 60

        # check if the slot is for 1 hour
        if min != 60:
            return Response(
            {"sCode": 422, "message": "Booking should be for 1 hour",},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        #check if there is a booking with select time slot and date
        operator_id = booking_info.first().operator_id

        info = Booking.objects.filter(operator_id = operator_id, start_time = booking_start_time, end_time = booking_end_time, booking_date=booking_date)

        # if the slot is already booked ask user to choose other slot
        if info:
           return Response(
            {"sCode": 400, "message": "Please select some other slot or date"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        # update booking info 

        booking_info.update(
            start_time = booking_start_time,
            end_time = booking_end_time,
            booking_date=booking_date,
            is_rescheduled = True
        )


        return Response(
            {"sCode": 200, "message": "Booking rescheduled successfully"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        parameters = [ViewBookingSerializer],
        responses={
            200: OpenApiTypes.OBJECT,
            412: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "SUCCESS",
                description="view slots for operator for specific date",
                value={
                    "sCode": 200,
                    "message": "Bookings for <booking_date> for <operator_id>",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 404,
                    "message": "Operator not registered",
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 412,
                    "message": "Future date not allowed",
                },
                response_only=True,
                status_codes=["412"],
            ),
        ],
    )
    def get(self, request):
        # to view bookings of operator
        serializer = ViewBookingSerializer(data=request.GET)
        if not serializer.is_valid():
            serializer_error = serializer.errors
            raise ValidationError(serializer_error)
        data = serializer.validated_data
        operator_id = data["operator_id"]
        booking_date = data.get("booking_date")
        view_booked_slots = data["view_booked_slots"]

        booked_slots = []
        avl_slots = ALL_SLOTS.copy()
        slots = []

        # if user doesnot give date then by default todays date will be taken 
        if not booking_date:
            booking_date = timezone.now().date()
        # check if the booking date future date
        if booking_date > timezone.now().date():
            return Response(
            {"sCode": 412, "message": "Future date not allowed",},
            status=status.HTTP_412_PRECONDITION_FAILED,
            )

        # check if operator exists in DB

        operator_info = Operator.objects.get(id=operator_id)

        if not operator_info:
            return Response(
            {"sCode": 404, "message": "Operator not registered",},
            status=status.HTTP_404_NOT_FOUND,
        )

        # fetch booking data for the operator
        booking_info = Booking.objects.filter(operator_id = operator_id, booking_date = booking_date, status = "booked")

        for booking in booking_info:
            booking_slot = str(booking.start_time) + "-" + str(booking.end_time)
            booked_slots.append(booking_slot)
            avl_slots.remove(booking_slot)
        
        # for the avl slots below function will merge continuous slots 
        if not view_booked_slots:
            n = len(avl_slots)
            split_slot = avl_slots[0].split('-')
            start_time = split_slot[0]
            end_time = split_slot[1]
            for i in range(1, n):
                split_slot = avl_slots[i].split('-')
                start_time_i = split_slot[0]
                end_time_i = split_slot[1]
                if end_time != start_time_i:
                    slots.append(str(start_time) + "-" + str(end_time))
                    start_time = start_time_i
                end_time = end_time_i
            if end_time == "00:00:00":
                end_time = "24:00:00"
            slots.append(str(start_time) + "-" + str(end_time))
        else:
            slots = booked_slots
                
        return Response(
            {"sCode": 200, "message": f"Bookings for {booking_date} for {operator_id}", "booking_date": booking_date, "slots": slots},
            status=status.HTTP_200_OK,
        )
       
class CancelBooking(APIView):  
    @extend_schema(
        responses={
            200: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
            412: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "SUCCESS",
                description="Booking cancelled successfully",
                value={
                    "sCode": 200,
                    "message": "Booking cancelled successfully",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 404,
                    "message": "Booking doesnot exists",
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "ERROR",
                description="ERROR",
                value={
                    "sCode": 412,
                    "message": "Booking already cancelled",
                },
                response_only=True,
                status_codes=["412"],
            ),
        ],
    )
    def delete(self, request, booking_id):

        # to cancel the booking 

        # check if the booking exist in DB
        booking_info = Booking.objects.filter(booking_id=booking_id)

        if not booking_info:
            return Response(
            {"sCode": 404, "message": "Booking doesnot exists",},
            status=status.HTTP_404_NOT_FOUND,
        )

        # check if booking is already cancelled
        if booking_info.first().status == "cancelled":
            return Response(
            {"sCode": 412, "message": "Booking already cancelled",},
            status=status.HTTP_404_NOT_FOUND,
        )

        # update booking info
        booking_info.update(
            is_cancelled = True,
            status="cancelled"
        )

        return Response(
            {"sCode": 200, "message": "Booking cancelled successfully"},
            status=status.HTTP_200_OK,
        )

class AddOperator(APIView):
    @extend_schema(
    request=OperatorSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "SUCCESS",
            description="Operator added succesfully",
            value={
                "sCode": 200,
                "message": "Operator succesfully added in DB",
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            "ERROR",
            description="ERROR",
            value={"sCode": 400, "message": "Operator already exists"},
            response_only=True,
            status_codes=["400"],
        ),
    ],
)
    def post(self, request):
        # add operator info in DB
        serializer = OperatorSerializer(data=request.data)
        if not serializer.is_valid():
            serializer_error = serializer.errors
            raise ValidationError(serializer_error)
        data = serializer.validated_data
        operator_name = data["name"]
        # check if operator already exisit in DB
        operator_info = Operator.objects.filter(operator_name = operator_name)

        if operator_info:
            return Response({"sCode": 400, "message": "Operator already exists"}, status=status.HTTP_400_BAD_REQUEST)

        id = str(uuid.uuid4().int)
        operator_id = id[:24]
        params = {
            "id": operator_id,
            "operator_name" : operator_name
        }
        Operator.objects.create(**params)

        return Response(
            {"sCode": 200, "message": "Operator succesfully added in DB", "operator_id": operator_id},
            status=status.HTTP_200_OK,
        )

