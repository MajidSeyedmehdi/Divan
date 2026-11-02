import jdatetime
from collections import defaultdict
from datetime import datetime, date, timedelta
from sound_recorders.shift_audit.calculation_setting.forms import HeaderForm
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from utils.db_connection import connect_db
logger = logging.getLogger(__name__)

def jalali_to_gregorian(date_value):
    if not date_value:
        return None

    try:
        if isinstance(date_value, (jdatetime.date, jdatetime.datetime)):
            return date_value.togregorian()

        year, month, day = map(
            int,
            str(date_value).replace("-", "/").split("/")
        )

        return jdatetime.date(
            year,
            month,
            day
        ).togregorian()

    except Exception as e:
        logger.error(f"Jalali date conversion error: {date_value} - {e}")
        return None

def gregorian_to_jalali(date_obj):
    if not date_obj:
        return None

    return jdatetime.date.fromgregorian(date=date_obj)

def gregorian_to_jalali_str(date_value, fmt="%Y/%m/%d"):
    """تبدیل تاریخ میلادی به رشته تاریخ شمسی"""
    if not date_value:
        return ""
    try:
        if isinstance(date_value, datetime):
            date_value = date_value.date()
        return jdatetime.date.fromgregorian(date=date_value).strftime(fmt)
    except Exception as e:
        logger.error(f"Error converting to Jalali: {date_value} - {e}")
        return ""

#شروع
def get_payroll_dates(cursor, id_final_payroll_calc=None, start_date=None, end_date=None):
    """
    استخراج تاریخ شروع و پایان بر اساس شناسه، ورودی مستقیم، یا جدیدترین دوره فعال
    """
    try:
        # ۱. اگر تاریخ‌ها مستقیماً ارسال شده باشند
        if start_date and end_date:
            start_date_g = jalali_to_gregorian(start_date) if isinstance(start_date, str) else start_date
            end_date_g = jalali_to_gregorian(end_date) if isinstance(end_date, str) else end_date
            return start_date_g, end_date_g, gregorian_to_jalali_str(start_date_g), gregorian_to_jalali_str(end_date_g)

        # ۲. اگر شناسه خاصی از جدول خلاصه محاسبه فرستاده شده باشد
        if id_final_payroll_calc:
            cursor.execute("""
                SELECT Start_date, End_date 
                FROM Tbl_Summary_Payroll_Calc 
                WHERE Id_final_payroll_calc = ? AND Active = 1 AND Del = 0
            """, [int(id_final_payroll_calc)])
        # ۳. در غیر این صورت، آخرین دوره فعال را برمی‌گرداند
        else:
            cursor.execute("""
                SELECT TOP 1 Start_date, End_date 
                FROM Tbl_Summary_Payroll_Calc 
                WHERE Active = 1 AND Del = 0
                ORDER BY Id_final_payroll_calc DESC
            """)

        row = cursor.fetchone()
        if not row or not row[0] or not row[1]:
            return None, None, None, None

        start_date_g, end_date_g = row[0], row[1]
        start_date_j = gregorian_to_jalali_str(start_date_g)
        end_date_j = gregorian_to_jalali_str(end_date_g)

        return start_date_g, end_date_g, start_date_j, end_date_j

    except Exception as e:
        logger.error(f"Error fetching payroll dates: {e}")
        return None, None, None, None
def get_user_manager_id(cursor, user):
    """پیدا کردن Id_manager کاربر بر اساس گروه کاربر در جنگو"""
    if not user.is_authenticated:
        return None
    group = user.groups.first()
    if not group:
        return None
    group_name = group.name

    cursor.execute("""
        SELECT TOP 1 Id_manager 
        FROM Tbl_Manager 
        WHERE Active = 1 AND Del = 0 
        AND ? LIKE '%' + Manager + '%'
    """, (group_name,))

    row = cursor.fetchone()
    return row[0] if row else None


def soundrecorders_managers_shift(request):
    """صفحه اصلی کارتابل و تاریخچه گزارش‌های مالی"""
    receive_rows = []
    history_rows = []
    active_tab = request.GET.get('tab', 'receive')
    show_last_column = True

    def get_report(cursor, read_start=None, read_end=None, manager_id=None):
        cursor.execute(
            "EXEC Sp_Soundrecorders_Financial_Report ?, ?, ?",
            (read_start, read_end, manager_id)
        )
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, row)) for row in cursor.fetchall()]

        for row in rows:
            if row.get("Start_date"):
                start_date = row["Start_date"]
                row["Start_date_j"] = jdatetime.date.fromgregorian(
                    date=start_date
                ).strftime("%Y/%m/%d")

            if row.get("End_date"):
                end_date = row["End_date"]
                row["End_date_j"] = jdatetime.date.fromgregorian(
                    date=end_date
                ).strftime("%Y/%m/%d")

        return rows

    with connect_db() as conn:
        cursor = conn.cursor()
        logged_in_manager_id = get_user_manager_id(cursor, request.user)

        if request.method == "GET":
            if logged_in_manager_id is not None:
                receive_rows = get_report(cursor, None, None, logged_in_manager_id)
            history_rows = get_report(cursor, None, None, None)

        elif request.method == "POST":
            action = request.POST.get("action")
            id_final_payroll_calc = request.POST.get("id_final_payroll_calc")

            if action in ["confirm", "reject"]:
                if not id_final_payroll_calc:
                    messages.error(request, "شناسه رکورد ارسال نشده است.")
                elif logged_in_manager_id is None:
                    messages.error(request, "مدیر مربوط به کاربر پیدا نشد.")
                else:
                    cursor.execute(
                        "SELECT Id_manager FROM Tbl_Summary_Payroll_Calc WHERE Id_final_payroll_calc = ?",
                        [int(id_final_payroll_calc)]
                    )
                    record = cursor.fetchone()
                    if record and str(record[0]) == str(logged_in_manager_id):
                        if action == "confirm":
                            cursor.execute("EXEC Sp_Inf_Manager_Confirm ?", [int(id_final_payroll_calc)])
                            conn.commit()
                            messages.success(request, "گزارش مالی تایید شد.")
                        else:
                            cursor.execute("EXEC Sp_Inf_Manager_Reject ?", [int(id_final_payroll_calc)])
                            conn.commit()
                            messages.success(request, "جهت اصلاح به مدیر صدابرداران برگردانده شد.")
                        return redirect(f"{request.path}?tab=receive")
                    else:
                        messages.error(request, "این رکورد در کارتابل شما قرار ندارد.")

            # بارگذاری مجدد داده‌ها
            if logged_in_manager_id is not None:
                receive_rows = get_report(cursor, None, None, logged_in_manager_id)
            history_rows = get_report(cursor, None, None, None)

    context = {
        "receive_rows": receive_rows,
        "history_rows": history_rows,
        "show_last_column": show_last_column,
        "logged_in_manager_id": logged_in_manager_id,
        "active_tab": active_tab,
    }

    return render(request, "main/includes/sound_recorders/sound_recorder_manager/shift_calculation.html", context)


def get_shift_details(request):
    """نمایش جزئیات شیفت بر اساس ID جدول یا تاریخ‌های ارسالی"""
    template_name = "main/includes/inf_manager/shift/shift_detail.html"
    id_final_payroll_calc = request.GET.get("id_final_payroll_calc")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # دریافت تاریخ مستقیم از دیتابیس با استفاده از ID رکورد
            if id_final_payroll_calc:
                start_date_greg, end_date_greg = get_payroll_dates(cursor, id_final_payroll_calc)
            else:
                start_date_greg = jalali_to_gregorian(start_date)
                end_date_greg = jalali_to_gregorian(end_date)
            if end_date_greg:
                # برای پوشش کامل روز آخر ماه در Stored Procedure
                end_date_greg = end_date_greg + timedelta(days=1)
            if not start_date_greg or not end_date_greg:
                return render(request, template_name, {
                    "error": "تاریخ شروع یا پایان معتبر یافت نشد.",
                    "data": [],
                    "table_columns": [],
                })

            cursor.execute("EXEC dbo.Sp_Soundrecorders_Shift_Details ?, ?", (start_date_greg, end_date_greg))

            rows = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()] if cursor.description else []

        table_columns = []
        seen_columns = set()

        for row in rows:
            network, id_network, id_shift, shift_name = row.get("Network"), row.get("Id_network"), row.get("Id_shift"), row.get("ShiftName")
            if None in (network, id_network, id_shift):
                continue

            key = (int(id_network), int(id_shift))
            if key not in seen_columns:
                seen_columns.add(key)
                table_columns.append({
                    "id_network": int(id_network),
                    "network": str(network).strip(),
                    "id_shift": int(id_shift),
                    "shift_name": str(shift_name).strip() if shift_name else str(id_shift),
                })

        table_columns.sort(key=lambda x: (x["id_network"], x["id_shift"]))

        shift_data = {}
        people_names = {}

        for row in rows:
            personal_id, id_network, id_shift = row.get("Id_personal"), row.get("Id_network"), row.get("Id_shift")
            if None in (personal_id, id_network, id_shift):
                continue

            p_id, n_id, s_id = int(personal_id), int(id_network), int(id_shift)
            people_names[p_id] = row.get("SoundRecorderName") or ""
            shift_data[(p_id, n_id, s_id)] = int(row.get("ShiftCount") or 0)

        data = []
        for p_id, person_name in people_names.items():
            cells = [shift_data.get((p_id, col["id_network"], col["id_shift"]), 0) for col in table_columns]
            data.append({"soundrecorder_name": person_name, "cells": cells})

        return render(request, template_name, {
            "data": data,
            "table_columns": table_columns,
            "start_date": start_date,
            "end_date": end_date,
        })

    except Exception as e:
        logger.error(f"Error in get_shift_details: {e}")
        return render(request, template_name, {
            "error": f"خطا در پردازش درخواست: {str(e)}",
            "data": [],
            "table_columns": [],
        })


def get_final_coating(request):
    """نمایش روکش نهایی بر اساس ID رکورد جدول"""
    template_name = "main/includes/inf_manager/shift/final_coating.html"
    id_final_payroll_calc = request.GET.get("id_final_payroll_calc")
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        data = []
        with connect_db() as conn:
            cursor = conn.cursor()

            if id_final_payroll_calc:
                start_date_greg, end_date_greg = get_payroll_dates(cursor, id_final_payroll_calc)
            else:
                start_date_greg = jalali_to_gregorian(start_date_str)
                end_date_greg = jalali_to_gregorian(end_date_str)
            if end_date_greg:
                # برای پوشش کامل روز آخر ماه در Stored Procedure
                end_date_greg = end_date_greg + timedelta(days=1)
            if not start_date_greg or not end_date_greg:
                return render(request, template_name, {"error": "تاریخ شروع یا پایان یافت نشد.", "data": []})

            cursor.execute("EXEC Sp_Soundrecorders_Final_Coating ?, ?", [start_date_greg, end_date_greg])

            if cursor.description:
                rows = cursor.fetchall()
                for row in rows:
                    data.append({
                        "national_code": row[2] if row[2] else '-',
                        "first_name": row[3] if row[3] else '-',
                        "last_name": row[4] if row[4] else '-',
                        "current_job": row[5] if row[5] else '-',
                        "levels": str(row[6]) if row[6] is not None else '-',
                        "final_baraovard": float(row[7]) if len(row) > 7 and row[7] is not None else 0
                    })

        return render(request, template_name, {
            "data": data,
            "start_date": start_date_str,
            "end_date": end_date_str,
        })

    except Exception as e:
        logger.error(f"Error in get_final_coating: {e}")
        return render(request, template_name, {"error": f"خطا در پردازش درخواست: {str(e)}", "data": []})

def get_network_coating(request):
    """نمایش روکش شبکه‌ها بر اساس ID رکورد"""
    template_name = "main/includes/inf_manager/shift/network_coating.html"

    id_final_payroll_calc = request.GET.get("id_final_payroll_calc")
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            if id_final_payroll_calc:
                # گرفتن مستقیم تاریخ میلادی ذخیره شده در دیتابیس بدون هیچ کم و زیاد کردنی
                start_date_greg, end_date_greg = get_payroll_dates(
                    cursor, id_final_payroll_calc
                )
            else:
                start_date_greg = jalali_to_gregorian(start_date_str)
                end_date_greg = jalali_to_gregorian(end_date_str)
            if end_date_greg:
                # برای پوشش کامل روز آخر ماه در Stored Procedure
                end_date_greg = end_date_greg + timedelta(days=1)

            if not start_date_greg or not end_date_greg:
                return render(
                    request,
                    template_name,
                    {
                        "error": "تاریخ شروع یا پایان معتبر یافت نشد.",
                        "data": [],
                        "id_final_payroll_calc": id_final_payroll_calc,
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                    }
                )

            # چاپ جهت تست و اطمینان در کنسول
            # برای ۳۱ تیر، end_date_greg باید 2026-07-22 باشد
            print("Sending to SP:", start_date_greg, end_date_greg)

            cursor.execute(
                "EXEC dbo.Sp_Soundrecorders_Network_Coating ?, ?",
                [start_date_greg, end_date_greg]
            )

            data = []
            if cursor.description:
                columns = [column[0].lower() for column in cursor.description]
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    data.append({
                        "id_network": item.get("id_network"),
                        "network": item.get("network") or "نامشخص",
                        "network_baravord": item.get("network_baraovard") or 0,
                        "id_final_payroll_calc": id_final_payroll_calc,
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                    })

        return render(
            request,
            template_name,
            {
                "data": data,
                "id_final_payroll_calc": id_final_payroll_calc,
                "start_date": start_date_str,
                "end_date": end_date_str,
            }
        )

    except Exception as e:
        logger.error(f"Error in get_network_coating: {e}")
        return render(
            request,
            template_name,
            {
                "error": f"خطا در پردازش اطلاعات: {str(e)}",
                "data": [],
                "id_final_payroll_calc": id_final_payroll_calc,
                "start_date": start_date_str,
                "end_date": end_date_str,
            }
        )
def get_network_detail(request):
    """نمایش جزئیات یک شبکه خاص بر اساس ID رکورد جدول و ID شبکه"""
    template_name = "main/includes/inf_manager/shift/network_detail_coating.html"
    id_final_payroll_calc = request.GET.get("id_final_payroll_calc")
    network_id = request.GET.get("network_id")
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    if not network_id:
        return render(request, template_name, {"error": "شناسه شبکه ارسال نشده است.", "shift_columns": [], "result_data": []})

    try:
        network_id = int(network_id)
        with connect_db() as conn:
            cursor = conn.cursor()

            if id_final_payroll_calc:
                start_date_greg, end_date_greg = get_payroll_dates(cursor, id_final_payroll_calc)
            else:
                start_date_greg = jalali_to_gregorian(start_date_str)
                end_date_greg = jalali_to_gregorian(end_date_str)
            if end_date_greg:
                # برای پوشش کامل روز آخر ماه در Stored Procedure
                end_date_greg = end_date_greg + timedelta(days=1)
            if not start_date_greg or not end_date_greg:
                return render(request, template_name, {"error": "تاریخ‌های بازه پیدا نشدند.", "shift_columns": [], "result_data": []})

            cursor.execute("""
                EXEC Sp_Soundrecorders_Network_Details_Coating
                    @StartDate=?,
                    @EndDate=?,
                    @NetworkId=?
            """, [start_date_greg, end_date_greg, network_id])

            cols = [column[0].lower() for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall() if cursor.description else []

            grouped_data = defaultdict(lambda: {
                "id_sound_recorder": None,
                "soundrecorder_name": "",
                "current_job": "-",
                "levels": "-",
                "shifts": {},
                "total_baraovard": 0,
            })

            shift_columns = []

            for row in rows:
                item = dict(zip(cols, row))
                rec_id = item.get("id_sound_recorder")
                if not rec_id:
                    continue

                person = grouped_data[rec_id]
                person["id_sound_recorder"] = rec_id
                person["soundrecorder_name"] = item.get("soundrecorder") or ""
                person["current_job"] = (item.get("current_job") or "-").strip()
                person["levels"] = item.get("levels") or "-"

                shift_name = item.get("shift_name") or (f"شیفت {item.get('id_shift')}" if item.get('id_shift') else "نامشخص")
                shift_name = str(shift_name).strip()

                if shift_name not in shift_columns:
                    shift_columns.append(shift_name)

                rate_value = item.get("shift_baraovard") if item.get("shift_baraovard") is not None else item.get("shift_base_rate")
                rate = float(rate_value or 0)
                count = int(item.get("shiftcount") or 1)

                person["shifts"][shift_name] = {"rate": rate, "count": count}
                person["total_baraovard"] += rate

            result_data = list(grouped_data.values())

        return render(request, template_name, {
            "shift_columns": shift_columns,
            "result_data": result_data,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "network_id": network_id,
        })

    except Exception as e:
        logger.error(f"Error in get_network_detail: {e}")
        return render(request, template_name, {"error": f"خطا در پردازش اطلاعات شبکه: {str(e)}", "shift_columns": [], "result_data": []})


def get_workflow_history(request):
    """تاریخچه گردش کار (مدال) بر اساس ID رکورد جدول"""
    payroll_id = request.GET.get('id')

    if not payroll_id or str(payroll_id).strip() in ['None', '', 'undefined']:
        return JsonResponse({'status': 'error', 'message': 'شناسه ارسال نشده است'}, status=400)

    try:
        payroll_id_int = int(payroll_id)
        history_list = []

        with connect_db() as conn:
            conn.add_output_converter(-155, lambda val: val.decode('utf-8') if isinstance(val, bytes) else str(val))
            cursor = conn.cursor()
            cursor.execute("EXEC dbo.Sp_Workflow_History ?", [payroll_id_int])
            rows = cursor.fetchall()

            for row in rows:
                action_date_shamsi = ''
                if len(row) > 2 and row[2]:
                    try:
                        raw_date_str = str(row[2]).strip()
                        clean_date_str = raw_date_str.split('+')[0].split('.')[0].strip()

                        if ' ' in clean_date_str:
                            g_date = datetime.strptime(clean_date_str, "%Y-%m-%d %H:%M:%S")
                            action_date_shamsi = jdatetime.datetime.fromgregorian(datetime=g_date).strftime("%Y/%m/%d - %H:%M")
                        else:
                            g_date = datetime.strptime(clean_date_str, "%Y-%m-%d")
                            action_date_shamsi = jdatetime.date.fromgregorian(date=g_date.date()).strftime("%Y/%m/%d")
                    except Exception:
                        action_date_shamsi = raw_date_str

                history_list.append({
                    'action_date': action_date_shamsi,
                    'workflow_action': str(row[3]) if len(row) > 3 and row[3] else '',
                    'description': str(row[4]) if len(row) > 4 and row[4] else '',
                    'manager': str(row[5]) if len(row) > 5 and row[5] else 'نامشخص'
                })

        return JsonResponse({'status': 'success', 'data': history_list})

    except Exception as e:
        logger.error(f"Error in get_workflow_history: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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
def run_final_audit(start_date, end_date):
    with connect_db() as conn:
        cursor = conn.cursor()
        # پیدا کردن تمام SP های SoundRecorders
        cursor.execute("""
            SELECT
                SCHEMA_NAME(schema_id) AS SchemaName,
                name AS ProcedureName
            FROM sys.procedures
            WHERE name LIKE '%SoundRecorders%'
            ORDER BY name
        """)

        procedures = cursor.fetchall()

        if procedures:
            for row in procedures:
                print(
                    "Schema:",
                    row[0],
                    "| Procedure:",
                    row[1]
                )
        else:
            print("!!! NO SOUNDRECORDERS PROCEDURES FOUND !!!")

        # بررسی مستقیم خود SP
        cursor.execute("""
            SELECT
                OBJECT_ID('dbo.Sp_SoundRecorders_Shift_Calculation', 'P')
        """)

        procedure_id = cursor.fetchone()[0]

        # فعلاً SP را اجرا می‌کنیم
        cursor.execute("""
            EXEC dbo.Sp_SoundRecorders_Shift_Calculation
                @StartDate = ?,
                @EndDate = ?
        """, (
            start_date,
            end_date
        ))

        # گرفتن نتیجه
        if cursor.description is None:
            return []

        columns = [column[0] for column in cursor.description]

        rows = cursor.fetchall()

        result_data = [
            dict(zip(columns, row))
            for row in rows
        ]

        print("Result data:", len(result_data))

        return result_data

def calculation_setting(request):
    result = []

    with connect_db() as conn:
        cursor = conn.cursor()

        # دریافت تاریخ‌ها یا شناسه دوره از درخواست (در صورت ارسال توسط کاربر)
        req_start = request.GET.get('start_date') or request.POST.get('start_date')
        req_end = request.GET.get('end_date') or request.POST.get('end_date')
        id_payroll = request.GET.get('id_final_payroll_calc') or request.POST.get('id_final_payroll_calc')

        # گرفتن تاریخ مربوط به همان ماه یا آخرین دوره فعال
        start_date, end_date, start_date_j, end_date_j = get_payroll_dates(
            cursor,
            id_final_payroll_calc=id_payroll,
            start_date=req_start,
            end_date=req_end
        )

        if not start_date or not end_date:
            messages.error(
                request,
                "دوره مالی مورد نظر یا دوره فعال در جدول Tbl_Summary_Payroll_Calc پیدا نشد."
            )
        else:
            if request.method == "POST":
                action = request.POST.get("action")
                if action == "calculate":
                    result = run_final_audit(start_date, end_date)

    context = {
        "start_date_j": start_date_j,
        "end_date_j": end_date_j,
        "result": result,
    }

    return render(
        request,
        "main/includes/sound_recorders/sound_recorder_manager/shift_calculation.html",
        context
    )
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

def person_shift_details(request, id_sound_recorder=None, start_date=None, end_date=None):
    # ۱. دریافت id_sound_recorder از URL path یا Query String
    id_sound_recorder = id_sound_recorder or request.GET.get('id_sound_recorder')

    # ۲. دریافت تاریخ‌ها از URL path یا Query String
    req_start = start_date or request.GET.get('start_date')
    req_end = end_date or request.GET.get('end_date')

    # کنترل عدم ارسال شناسه صدابردار
    if not id_sound_recorder:
        messages.error(request, "شناسه صدابردار مشخص نشده است.")
        return redirect('sound_recorders:soundrecorders:soundrecorders_managers')

    with connect_db() as conn:
        cursor = conn.cursor()

        # استخراج دقیق تاریخ‌های همان ماه
        start_date_g, end_date_g, start_date_j, end_date_j = get_payroll_dates(
            cursor,
            start_date=req_start,
            end_date=req_end
        )

        cursor.execute("""
            EXEC Sp_GetPersonShiftDetails
                @id_sound_recorder = ?,
                @start_date = ?,
                @end_date = ?
        """, [
            int(id_sound_recorder),
            start_date_g,
            end_date_g
        ])

        columns = [column[0] for column in cursor.description]
        shifts = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # تبدیل تاریخ‌های هر شیفت به روز هفته و شمسی
        for row in shifts:
            original_date = row.get('Shift_date')
            row['Weekday'] = get_persian_weekday(original_date)
            row['Shift_date'] = gregorian_to_jalali_str(original_date)

        first_name = shifts[0].get('First_name') or '' if shifts else ''
        last_name = shifts[0].get('Last_name') or '' if shifts else ''

        return render(
            request,
            'main/includes/sound_recorders/shift_audit/person_shift_details/person_shift_details.html',
            {
                'id_sound_recorder': id_sound_recorder,
                'first_name': first_name,
                'last_name': last_name,
                'shifts': shifts,
                'start_date': start_date_j,
                'end_date': end_date_j,
            }
        )