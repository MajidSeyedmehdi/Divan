
from django.db import connection

from django.shortcuts import render, redirect

from utils.db_connection import connect_db


# خواندن دوره مالی فعال
def get_financial_period():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 1 Start_date, End_date
            FROM Tbl_Financial_Period
            WHERE Active = 1 AND Del = 0
            ORDER BY Id_period DESC
        """)
        row = cursor.fetchone()

        if row:
            return row[0], row[1]
    return None, None

def to_jalali(date_value):
    if not date_value:
        return "-"

    try:
        jalali = jdatetime.date.fromgregorian(date=date_value)
        return jalali.strftime("%Y/%m/%d")
    except Exception:
        return str(date_value)

import jdatetime


def get_persian_weekday(date_value):
    if not date_value:
        return "-"
    try:
        jalali_date = jdatetime.date.fromgregorian(date=date_value)

        weekdays = {
            0: "شنبه",
            1: "یکشنبه",
            2: "دوشنبه",
            3: "سه‌شنبه",
            4: "چهارشنبه",
            5: "پنجشنبه",
            6: "جمعه",
        }

        return weekdays.get(jalali_date.weekday(), "-")
    except Exception:
        return str(date_value)



def person_shift_details(request, id_sound_recorder, start_date=None, end_date=None):

    # اگر تاریخ‌ها از URL نیامده باشند، دوره مالی فعال را بگیر
    if not start_date or not end_date:
        start_date, end_date = get_financial_period()

        # if start_date:
        #     start_date = gregorian_to_jalali(start_date)
        #
        # if end_date:
        #     end_date = gregorian_to_jalali(end_date)

    with connection.cursor() as cursor:

        cursor.execute("""
            EXEC Sp_GetPersonShiftDetails
                @id_sound_recorder = %s,
                @start_date = %s,
                @end_date = %s
        """, [
            id_sound_recorder,
            start_date,
            end_date
        ])

        columns = [column[0] for column in cursor.description]

        shifts = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    # تبدیل تاریخ Shift_date هر ردیف به شمسی
    if start_date:
        start_date = to_jalali(start_date)

    if end_date:
        end_date = to_jalali(end_date)



    # تبدیل تاریخ Shift_date هر ردیف به شمسی
    for row in shifts:
        original_date = row.get('Shift_date')

        row['Weekday'] = get_persian_weekday(original_date)
        row['Shift_date'] = to_jalali(original_date)

    # نام و نام خانوادگی از اولین رکورد
    first_name = ''
    last_name = ''

    if shifts:
        first_name = shifts[0].get('First_name') or ''
        last_name = shifts[0].get('Last_name') or ''
    total_baraovard = sum(
        row.get('Total_rate', 0) for row in shifts if not row.get('Mandatory_shift')
    )
    return render(
        request,
        'main/includes/sound_recorders/shift_audit/person_shift_details/person_shift_details.html',
        {
            'id_sound_recorder': id_sound_recorder,
            'first_name': first_name,
            'last_name': last_name,
            'shifts': shifts,
            'start_date': start_date,
            'end_date': end_date,
            'total_baraovard': total_baraovard,
        }
    )