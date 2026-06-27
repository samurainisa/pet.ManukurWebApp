from datetime import date, datetime, timedelta

from django.utils import timezone

from scheduling.models import Appointment, TimeOffBlock, WorkScheduleRule


def has_overlap(start_datetime, end_datetime, exclude_appointment_id=None) -> bool:
    queryset = Appointment.objects.filter(
        status__in=Appointment.ACTIVE_SLOT_STATUSES,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    )
    if exclude_appointment_id:
        queryset = queryset.exclude(pk=exclude_appointment_id)
    return queryset.exists()


def has_time_off_overlap(start_datetime, end_datetime) -> bool:
    return TimeOffBlock.objects.filter(
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
    ).exists()


def get_day_bounds(day: date):
    rule = WorkScheduleRule.objects.filter(weekday=day.weekday()).first()
    tz = timezone.get_current_timezone()
    if not rule:
        if day.weekday() == 6:
            return None
        day_start = timezone.make_aware(datetime.combine(day, datetime.min.time().replace(hour=9)), tz)
        day_end = timezone.make_aware(datetime.combine(day, datetime.min.time().replace(hour=18)), tz)
        return day_start, day_end

    if not rule.is_working_day:
        return None

    day_start = timezone.make_aware(datetime.combine(day, rule.start_time), tz)
    day_end = timezone.make_aware(datetime.combine(day, rule.end_time), tz)
    return day_start, day_end


def is_inside_working_hours(start_datetime, end_datetime) -> bool:
    if timezone.localdate(start_datetime) != timezone.localdate(end_datetime):
        return False

    bounds = get_day_bounds(timezone.localdate(start_datetime))
    if not bounds:
        return False

    day_start, day_end = bounds
    return start_datetime >= day_start and end_datetime <= day_end


def generate_available_slots(day: date, duration_min: int, step_min: int = 30):
    bounds = get_day_bounds(day)
    if not bounds:
        return []

    day_start, day_end = bounds
    now = timezone.now()
    current = day_start
    slot_duration = timedelta(minutes=duration_min)
    step = timedelta(minutes=step_min)
    result = []

    while current + slot_duration <= day_end:
        end_slot = current + slot_duration
        is_in_past = end_slot <= now

        if not is_in_past and not has_overlap(current, end_slot) and not has_time_off_overlap(current, end_slot):
            result.append(current)

        current += step

    return result
