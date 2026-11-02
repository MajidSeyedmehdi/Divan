import jdatetime
from django.shortcuts import render, redirect
from .forms import HeaderForm
from utils.db_connection import connect_db
from django.contrib import messages

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

def gregorian_to_jalali(date_obj):
    if not date_obj:
        return None

    return jdatetime.date.fromgregorian(date=date_obj)


def fetch_rows(start_date=None, end_date=None):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "EXEC Sp_Calculation_Read ?, ?",
            (start_date, end_date)
        )

        cols = [c[0] for c in cursor.description]

        return [
            dict(zip(cols, row))
            for row in cursor.fetchall()
        ]

def run_final_audit(user_name):
    with connect_db() as conn:
        cursor = conn.cursor()

        # ۱. دریافت PeriodId فعال
        cursor.execute("SELECT TOP (1) Id_period FROM Tbl_Financial_Period WHERE Active = 1 AND Del = 0")
        period_row = cursor.fetchone()
        if not period_row:
            return []
        period_id = period_row[0]

        # ۲. اجرای دو استور اول
        cursor.execute("EXEC Sp_GenerateRateRulesByPeriod @PeriodId = ?", (period_id,))
        cursor.execute("EXEC Sp_GenerateShiftPayrollCalcByPeriod @PeriodId = ?, @UserName = ?", (period_id, user_name))

        # ۳. اجرای استور اصلی و خواندن سریع خروجی آن
        cursor.execute("EXEC Sp_Calculate_SoundRecorder_Payroll @PeriodId = ?", (period_id,))
        columns = [column[0] for column in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        result_data = [dict(zip(columns, row)) for row in rows]

        # ۴. اجرای استور پایانی
        cursor.execute("EXEC Sp_Insert_Sum_Pay_Calc @PeriodId = ?", (period_id,))

        conn.commit()

        # بازگرداندن داده‌های استور سوم
        return result_data


def save_final_audit_results(user_name):
    """
    اجرای تابع یا کوئری ذخیره‌سازی نهایی از جدول محاسباتی/تمپ به جدول اصلی دیتابیس
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        # در صورت داشتن Stored Procedure مجزا برای ذخیره نهایی:
        # cursor.execute("EXEC Sp_Save_Final_Payroll_Audit @UserName = ?", (user_name,))

        # نکته: استور Sp_Calculate_SoundRecorder_Payroll شما همین الان هم
        # دستور MERGE دارد و اطلاعات را در جدول Tbl_Shift_Payroll_Calc بروز می‌کند.
        conn.commit()

def calculation_setting(request):
    start_db, end_db = get_financial_period()

    default_start = gregorian_to_jalali(start_db)
    default_end = gregorian_to_jalali(end_db)

    read_start = start_db.strftime("%Y-%m-%d") if start_db else None
    read_end = end_db.strftime("%Y-%m-%d") if end_db else None

    result = []

    if request.method == "POST":
        header_form = HeaderForm(request.POST)
        user_name = request.user.username if request.user.is_authenticated else "system"
        action = request.POST.get("action")

        if action == "calculate":
            # ۱. اجرای محاسبات ۳ استور و نمایش مقادیر جدید
            result=run_final_audit(user_name)
            # messages.success(request, "محاسبات با موفقیت انجام شد.")
            # print('hi')
        elif action == "save":
            # ۲. کلیک روی دکمه ذخیره: ابتدا محاسبات را اجرا کرده سپس ذخیره می‌کند
            result = run_final_audit(user_name)
            save_final_audit_results(user_name)
            messages.success(request, "اطلاعات با موفقیت در دیتابیس ذخیره شد.")

    else:
        header_form = HeaderForm(initial={
            "start_date": default_start,
            "end_date": default_end
        })
        # حالت عادی قبل از زدن دکمه: خواندن داده‌های اولیه از Sp_Calculation_Read
        result = fetch_rows(read_start, read_end)

    context = {
        "header_form": header_form,
        "result": result,
    }

    return render(
        request,
        "main/includes/sound_recorders/shift_audit/calculation_setting/calculation_setting.html",
        context
    )

# def calculation_setting(request):
#
#     # -----------------------------
#     # خواندن دوره مالی فعال
#     # -----------------------------
#
#     start_db, end_db = get_financial_period()
#
#     # تاریخ جلالی برای فرم
#     default_start = gregorian_to_jalali(start_db)
#     default_end = gregorian_to_jalali(end_db)
#
#     # # تاریخ میلادی برای SP
#     read_start = start_db.strftime("%Y-%m-%d") if start_db else None
#     read_end = end_db.strftime("%Y-%m-%d") if end_db else None
#
#     result = []
#     # -----------------------------
#     # فرم هدر
#     # -----------------------------
#     if request.method == "POST":
#
#         header_form = HeaderForm(request.POST)
#         user_name = request.user.username if request.user.is_authenticated else "system"
#         if header_form.is_valid():
#
#             start_date_j = header_form.cleaned_data.get("start_date")
#             end_date_j = header_form.cleaned_data.get("end_date")
#
#
#
#
#             action = request.POST.get("action")
#
#             # -----------------------------
#             # ذخیره اطلاعات
#             # -----------------------------
#             if action == "calculate":
#                 with connect_db() as conn:
#                     cursor = conn.cursor()
#
#                     # 1. اصلاح پاس دادن پارامتر با کاما (user_name,)
#                     cursor.execute("EXEC Sp_Final_Shift_Audit @UserName = ?", (user_name,))
#
#                     # 2. بررسی اینکه آیا SP خروجی (Select) برمی‌گرداند یا خیر
#                     if cursor.description:
#                         cols = [c[0] for c in cursor.description]
#                         # 3. ساخت لیستی از دیکشنری‌ها به صورت List Comprehension
#                         result = [dict(zip(cols, row)) for row in cursor.fetchall()]
#                     else:
#                         result = []
#
#                     conn.commit()
#                     # دریافت اطلاعات جدید جدول پس از محاسبه
#
#     else:
#
#     # مقداردهی اولیه فرم استاندارد جنگو
#
#         header_form = HeaderForm(initial={
#
#             "start_date": default_start,
#
#             "end_date": default_end
#
#         })
#         # اجرای fetch_rows در زمان باز شدن صفحه
#     # خواندن جدول
#     # -----------------------------
#     result = fetch_rows(read_start, read_end)
#
#     # # اگر خالی بود
#     # if not result:
#     #     result = fetch_rows(None, None)
#     context = {
#         "header_form": header_form,
#         "result": result,
#     }
#
#     return render(
#         request,
#         "main/includes/sound_recorders/shift_audit/calculation_setting/calculation_setting.html",
#         context
#     )