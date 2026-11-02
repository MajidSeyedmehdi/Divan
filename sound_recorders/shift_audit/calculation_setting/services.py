import jdatetime as jd
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from .models import Network_Shift, Shift

weekdays_fa = {
    "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
    "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
    "Thursday": "پنجشنبه", "Friday": "جمعه",
}

def build_shift_table(selected_date, selected_network=None, selected_sound_recorder=None):
    """
    یک تابع کمکی برای ساخت جدول شیفت ماه
    قابل استفاده در چند ویو با ورودی‌های متفاوت.
    """

    # اگر تاریخ انتخاب نشده بود → امروز
    selected_date = selected_date or jd.date.today()

    # استخراج سال و ماه
    year, month = selected_date.year, selected_date.month

    # روز اول و آخر ماه جلالی
    first_day_j = jd.date(year, month, 1)
    next_month_j = jd.date(year + 1, 1, 1) if month == 12 else jd.date(year, month + 1, 1)
    last_day_j = next_month_j - timedelta(days=1)
    first_day_g = first_day_j.togregorian()
    last_day_g = last_day_j.togregorian()

    # تاریخ‌های ماه قبل
    first_prev = first_day_g - relativedelta(months=1)
    last_prev = last_day_g - relativedelta(months=1)

    # گرفتن شیفت‌های شبکه
    shifts = []
    if selected_network:
        shift_ids = Network_Shift.objects.filter(id_network=selected_network).values_list('id_shift', flat=True)
        shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by('shift_number')

    # ساخت جدول روزها
    daily_forms = []
    for d in range(1, last_day_j.day + 1):
        j_day = jd.date(year, month, d)
        g_day = j_day.togregorian()

        daily_forms.append({
            "jalali_date": j_day.strftime('%Y/%m/%d'),
            "jalali_day_name": weekdays_fa[j_day.strftime('%A')],
            "greg_date": g_day.strftime('%Y-%m-%d'),
            "sound_recorder": selected_sound_recorder,   # ✅ اضافه کردن پارامتر جدید
        })

    return {
        "daily_forms": daily_forms,
        "shifts": shifts,
        "selected_date": selected_date,
        "sound_recorder": selected_sound_recorder,
    }
