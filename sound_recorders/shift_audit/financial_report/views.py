import jdatetime
from collections import defaultdict

from django.contrib import messages
from django.shortcuts import render,redirect


from information.inf_manager.shift.views import get_user_manager_id
from sound_recorders.shift_audit.financial_report.forms import HeaderForm
from utils.db_connection import connect_db
from django.http import JsonResponse
from datetime import datetime, timedelta


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
        return row if row else (None, None)

def gregorian_to_jalali(date_obj):
    if not date_obj:
        return None
    return jdatetime.date.fromgregorian(date=date_obj)


def safe_jalali_to_gregorian(date_str):
    if not date_str:
        return None
    try:
        # استانداردسازی جداکننده‌ها
        clean_str = str(date_str).strip().replace('/', '-')
        parts = [int(p) for p in clean_str.split('-') if p.isdigit()]

        if len(parts) == 3:
            # اگر سال اول بود (مثلا 1403-02-01)
            if parts[0] > 1300:
                y, m, d = parts[0], parts[1], parts[2]
            # اگر روز اول بود (مثلا 01-02-1403)
            else:
                d, m, y = parts[0], parts[1], parts[2]

            return jdatetime.date(y, m, d).togregorian().strftime('%Y-%m-%d')
    except Exception as e:
        print("Date conversion error:", e)
    return date_str  # در صورت بروز خطا، خود ورودی را برمی‌گرداند

def financial_report(request):

    receive_rows = []
    history_rows = []
    active_tab = request.GET.get('tab', 'history')
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
                row["Start_date_j"] = jdatetime.date.fromgregorian(date=start_date).strftime("%Y/%m/%d")

            if row.get("End_date"):
                end_date = row["End_date"]
                actual_end_date = end_date - timedelta(days=1)
                row["End_date_j"] = jdatetime.date.fromgregorian(date=actual_end_date).strftime("%Y/%m/%d")
                row["End_date_calc_j"] = jdatetime.date.fromgregorian(date=end_date).strftime("%Y/%m/%d")

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

    return render(request, "main/includes/sound_recorders/shift_audit/financial_report/financial_report.html", context)


def get_workflow_history(request):
    payroll_id = request.GET.get('id')
    if not payroll_id or payroll_id == 'undefined':
        return JsonResponse({'status': 'error', 'message': 'شناسه نامعتبر است'})

    history_list = []
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            # فراخوانی استور پروسیجر
            cursor.execute("EXEC dbo.Sp_Workflow_History @Id_final_payroll_calc = ?", [payroll_id])
            rows = cursor.fetchall()

            for row in rows:
                # row[2] همان Action_Date است
                raw_date_str = str(row[2]) if len(row) > 2 and row[2] else ''
                action_date_shamsi = raw_date_str

                if raw_date_str:
                    try:
                        clean_date_str = raw_date_str.split('.')[0] # حذف میلی‌ثانیه در صورت وجود
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
                    'workflow_action': str(row[3]) if len(row) > 3 and row[3] else '-',
                    'description': str(row[4]) if len(row) > 4 and row[4] else '-',
                    'manager': str(row[5]) if len(row) > 5 and row[5] else 'نامشخص'
                })

        return JsonResponse({'status': 'success', 'data': history_list})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
def convert_to_gregorian_if_needed(date_str):
    if not date_str:
        return None
    try:
        clean_str = str(date_str).strip().replace('/', '-')
        parts = [int(p) for p in clean_str.split('-') if p.isdigit()]

        if len(parts) == 3:
            year, month, day = parts[0], parts[1], parts[2]

            # اگر سال بالای ۱۷۰۰ باشد، یعنی تاریخ از قبل میلادی است!
            if year > 1700:
                return f"{year:04d}-{month:02d}-{day:02d}"

            # اگر سال شمسی باشد (مثلاً ۱۴۰۳ یا ۱۴۰۵)
            elif 1300 <= year <= 1500:
                return jdatetime.date(year, month, day).togregorian().strftime("%Y-%m-%d")
    except Exception as e:
        print("Date parse error:", e)

    return date_str


def get_final_coating(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return JsonResponse({'status': 'error', 'message': 'تاریخ شروع یا پایان ارسال نشده است'}, status=400)

    try:
        # تبدیل هوشمند تاریخ (در صورت نیاز)
        start_date_greg = convert_to_gregorian_if_needed(start_date_str)
        end_date_greg = convert_to_gregorian_if_needed(end_date_str)

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Sp_Soundrecorders_Final_Coating ?, ?", [start_date_greg, end_date_greg])
            rows = cursor.fetchall()

            data = []
            for row in rows:
                data.append({
                    "national_code": row[2] if row[2] else '-',
                    "first_name": row[3] if row[3] else '-',
                    "last_name": row[4] if row[4] else '-',
                    "current_job": row[5] if row[5] else '-',
                    "levels": str(row[6]) if row[6] is not None else '-',
                    "final_baraovard": float(row[7]) if len(row) > 7 and row[7] is not None else 0
                })

        return JsonResponse({
            "status": "success",
            "data": data
        })

    except Exception as e:
        print("Error in get_final_coating:", str(e))
        return JsonResponse({'status': 'error', 'message': f"خطا در دیتابیس: {str(e)}"}, status=500)


def get_network_coating(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        return JsonResponse({'status': 'error', 'message': 'تاریخ ارسال نشده است'}, status=400)

    try:
        start_date_greg = safe_jalali_to_gregorian(start_date_str)
        end_date_greg = safe_jalali_to_gregorian(end_date_str)

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC Sp_Soundrecorders_Network_Coating ?, ?", [start_date_greg, end_date_greg])

            cols = [column[0].lower() for column in cursor.description]
            rows = cursor.fetchall()

            data = []
            for row in rows:
                item = dict(zip(cols, row))
                data.append({
                    "id_network": item.get("id_network"),
                    "network": item.get("network") or '-',
                    "network_baravord": float(item.get("network_baraovard") or 0)
                })

        return JsonResponse({
            "status": "success",
            "data": data
        })

    except Exception as e:
        print("Error in get_network_coating:", str(e))
        return JsonResponse({'status': 'error', 'message': f"خطا در دیتابیس: {str(e)}"}, status=500)


def get_network_detail(request):
    network_id = request.GET.get('network_id')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not network_id or not start_date_str or not end_date_str:
        return JsonResponse({'status': 'error', 'message': 'پارامترهای ورودی کامل نیستند'}, status=400)

    try:
        start_date_greg = safe_jalali_to_gregorian(start_date_str)
        end_date_greg = safe_jalali_to_gregorian(end_date_str)

        if not start_date_greg or not end_date_greg:
            return JsonResponse({'status': 'error', 'message': 'فرمت تاریخ‌های ورودی معتبر نیست.'}, status=400)

        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "EXEC Sp_Soundrecorders_Network_Details_Coating @StartDate=?, @EndDate=?, @NetworkId=?",
                [start_date_greg, end_date_greg, int(network_id)]
            )

            cols = [column[0].lower() for column in cursor.description]
            rows = cursor.fetchall()

            grouped_data = defaultdict(lambda: {
                'soundrecorder_name': '',
                'current_job': '-',
                'levels': '-',
                'shifts': {},
                'total_baraovard': 0
            })

            shift_columns = []

            for row in rows:
                item = dict(zip(cols, row))
                rec_id = item.get("id_sound_recorder")

                if not rec_id:
                    continue

                person = grouped_data[rec_id]
                person['soundrecorder_name'] = item.get("soundrecorder") or ''
                person['current_job'] = item.get("current_job") or '-'
                person['levels'] = item.get("levels") or '-'

                shift_name = item.get("shift_name") or f"شیفت {item.get('id_shift') or ''}"

                if shift_name not in shift_columns:
                    shift_columns.append(shift_name)

                rate = float(item.get("shift_baraovard") or item.get("shift_base_rate") or 0)
                count = int(item.get("shiftcount") or 1)

                person['shifts'][shift_name] = {
                    'rate': rate,
                    'count': count
                }

                person['total_baraovard'] += rate

            result_data = []
            for rec_id, p_info in grouped_data.items():
                result_data.append({
                    "id_sound_recorder": rec_id,
                    "soundrecorder_name": p_info['soundrecorder_name'],
                    "current_job": p_info['current_job'],
                    "levels": p_info['levels'],
                    "shifts": p_info['shifts'],
                    "total_baraovard": p_info['total_baraovard']
                })

        return JsonResponse({
            "status": "success",
            "shift_columns": shift_columns,
            "data": result_data
        })

    except Exception as e:
        print("Error in get_network_detail:", str(e))
        return JsonResponse({'status': 'error', 'message': f"خطا در دیتابیس: {str(e)}"}, status=500)
