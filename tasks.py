"""
Task are defined as functions, these functions will be imported in a scheduled management command (app_name/management/commands).
The schedule depends on the commands name suffix:
_every_morning are executed every morning on business days at 7 a.m. UTC from Monday to Friday
_every_week are executed every Monday of the week at 8 a.m. UTC
_every_month are executed the first day of the month at 9 a.m. UTC

Please import the task inside the command which suits your desirable schedule.
"""

from datetime import timedelta
from django.utils import timezone
from common.email_notifications import send_email
from aif.models import (
    Aif,
    AifStatusChoices,
)
from aif.api_views import get_aif_status
from aif.roles import  SALES_OPS_USER
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
User = get_user_model()

REMINDER_DAYS = 7

def send_pending_approval_notifications():
    """
    Sends reminder emails every morning for AIFs that have
    remained in AWAITING_VALIDATION for more than REMINDER_DAYS.
    """
    reminder_date = timezone.now() - timedelta(days=REMINDER_DAYS)
    
    for aif in Aif.objects.all():
        current_status = get_aif_status(aif)
        if current_status.status != AifStatusChoices.AWAITING_VALIDATION:
            continue

        status_date = (
            aif.meta_edited_date
            if aif.meta_edited_date
            else aif.meta_created_date
        )

        if status_date > reminder_date:
            continue

        notify_requester_reminder(aif)



def notify_requester_reminder(aif):
    """
    Sends a reminder email to the requester (creator of the AIF)
    when the AIF has been in AWAITING_VALIDATION for more than
    7 days.
    """
    if not aif.meta_created_by:
        return

    if not aif.meta_created_by.email:
        return
    
    group = Group.objects.get(name=SALES_OPS_USER)
    cc = ";".join(
        User.objects.filter(groups=group)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    send_email(
        to=aif.meta_created_by.email,
        subject=(
            f"Reminder - Promotion Ref "
            f"{aif.aif_id} awaiting validation"
        ),
        body=f"""
                Dear {aif.meta_created_by.first_name},<br><br>

                Your Promotion Request <b>{aif.aif_id}</b>
                has been in <b>Awaiting Validation</b>
                for more than <b>{REMINDER_DAYS} days</b>.<br><br>

                Please validate your ONINVOICE promotion request
                within 12 hours.<br><br>

                Kind Regards<br>
                Rev Sales Ops Team
                """,
            cc =cc
            )
            

