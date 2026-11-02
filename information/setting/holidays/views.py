import jdatetime as jd
from datetime import timedelta
from django.shortcuts import render
from .forms import HeaderForm
from utils.db_connection import connect_db


def holiday_view(request):

    # -----------------------------
    # 1️⃣ گرفتن تاریخ انتخاب شده
    # -----------------------------
    selected_date = jd.date.today()
    p_date_str = request.POST.get('p_date')

    if p_date_str:
        try:
            sep = '/' if '/' in p_date_str else '-'
            year, month, day = map(int, p_date_str.split(sep))
            selected_date = jd.date(year, month, day)
        except:
            selected_date = jd.date.today()

    year, month = selected_date.year, selected_date.month

    # -----------------------------
    # 2️⃣ ساخت روزهای ماه
    # -----------------------------
    first_day_j = jd.date(year, month, 1)
    next_month_j = jd.date(year + 1, 1, 1) if month == 12 else jd.date(year, month + 1, 1)
    last_day_j = next_month_j - timedelta(days=1)

    weekdays_fa = {
        "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه", "Friday": "جمعه",
    }

    daily_forms = []
    for d in range(1, last_day_j.day + 1):
        j_day = jd.date(year, month, d)
        daily_forms.append({
            'jalali_date': j_day.strftime('%Y/%m/%d'),
            'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
            'holiday_desc': None
        })

    action = request.POST.get('action')

    # -----------------------------
    # 3️⃣ عملیات ذخیره
    # -----------------------------
    if action == 'save':
        checked_days = request.POST.getlist('holiday_days')

        try:
            with connect_db() as conn:
                cursor = conn.cursor()

                for day in daily_forms:
                    shamsi_date = day['jalali_date']
                    is_holiday = shamsi_date in checked_days

                    desc_field = f"desc_{shamsi_date}"
                    description = request.POST.get(desc_field, '')

                    holiday_type = "تعطیل رسمی" if is_holiday else None
                    is_active = 1 if is_holiday else 0

                    j = jd.datetime.strptime(shamsi_date, '%Y/%m/%d')
                    g_date = j.togregorian()

                    cursor.execute("""
                        EXEC Sp_Insert_Holidays
                            @holiday_date = ?,
                            @shamsi_date = ?,
                            @holiday_type = ?,
                            @description = ?,
                            @is_active = ?
                    """, (g_date, shamsi_date, holiday_type, description, is_active))

                conn.commit()

        except Exception as e:
            print("❌ SQL Error:", e)

    # -----------------------------
    # 4️⃣ گرفتن داده‌ها از دیتابیس برای نمایش
    # -----------------------------
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Shamsi_date, Description
                FROM Tbl_Holidays
                WHERE Active = 1
                  AND Shamsi_date BETWEEN ? AND ?
            """, (
                first_day_j.strftime('%Y/%m/%d'),
                last_day_j.strftime('%Y/%m/%d')
            ))

            rows = cursor.fetchall()
            shamsi_map = {row[0]: row[1] for row in rows}

    except Exception as e:
        # print("❌ SQL Error:", e)
        shamsi_map = {}

    for day in daily_forms:
        day['holiday_desc'] = shamsi_map.get(day['jalali_date'])

    # -----------------------------
    # 5️⃣ فرم بردکرامپ
    # -----------------------------
    form = HeaderForm(initial={'p_date': selected_date})

    context = {
        'form': form,
        'daily_forms': daily_forms,
        'selected_date_str': selected_date.strftime('%Y/%m/%d'),
    }

    return render(request, 'main/includes/setting/holidays/holidays.html', context)
