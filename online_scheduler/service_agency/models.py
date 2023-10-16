from django.db import models

# Create your models here.


class Booking(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    booking_id = models.CharField(primary_key=True, max_length=255)
    operator_id = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_rescheduled = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        db_table="booking"
        indexes = [
            models.Index(fields=["booking_id"], name="booking_id_idx"),
            models.Index(fields=["operator_id"], name="operator_id_idx")
        ]

class Operator(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    id = models.CharField(primary_key=True, max_length=255)
    operator_name = models.CharField(max_length=100)

    class Meta:
        db_table="operator"