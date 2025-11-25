import jdatetime
import pyodbc
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db import connection,DatabaseError
from .forms import HeaderForm
from .models import Shift, Network_Shift
import jdatetime as jd
from datetime import timedelta, datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from utils.db_connection import connect_db
from dateutil.relativedelta import relativedelta

def create_new(request):
    header_form = HeaderForm(request.POST or None)
    selected_network = None
    selected_date = jd.date.today()

    if request.method == "POST" and header_form.is_valid():
        selected_date = header_form.cleaned_data.get('p_date') or selected_date
        selected_network = header_form.cleaned_data.get('network')
        action = request.POST.get('action')
        # 🔹 تعیین تاریخ درست بسته به دکمه
        # if action == 'previous_month':
        #     greg_date = selected_date.togregorian()
        #     prev_greg_date = greg_date - relativedelta(months=1)
        #     selected_date = jd.date.fromgregorian(date=prev_greg_date)
    # تاریخ‌ها برای ماه انتخاب‌شده
    year, month = selected_date.year, selected_date.month
    # تاریخ‌های ماه جاری
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

    weekdays_fa = {
        "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه", "Friday": "جمعه",
    }
    # ساخت جدول روزهای ماه

    daily_forms = []
    for d in range(1, last_day_j.day + 1):
        j_day = jd.date(year, month, d)
        g_day = j_day.togregorian()
        daily_forms.append({
            'jalali_date': j_day.strftime('%Y/%m/%d'),
            'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
            'greg_date': g_day.strftime('%Y-%m-%d')
        })

    # اجرای Stored Procedure برای نمایش داده‌ها
    shift_lookup = {}
    if selected_network:
        network_id = selected_network.id_network if hasattr(selected_network, 'id_network') else int(selected_network)
        action = request.POST.get('action')
        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                # 🔹 نمایش جدول ابتدایی
                if action == 'current_month':
                    cursor.execute(
                        "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?",
                        (first_day_g, last_day_g, network_id)
                    )
                elif action == 'final_month':
                    cursor.execute(
                        "EXEC Sp_ShiftShow_Final @start_date=?, @end_date=?, @id_network=?",
                        (first_day_g, last_day_g, network_id)
                    )
                elif action == 'transfer_previous':
                    # ابتدا شیفت‌های ماه قبل
                    cursor.execute(
                        "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?",
                        (first_prev, last_prev, network_id)
                    )

                # گرفتن خروجی
                cols = [column[0] for column in cursor.description]
                rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
                # 🟦 لیست تاریخ‌های مجاز (روزهای ماه فعلی)
                valid_dates = {d['greg_date'] for d in daily_forms}
                # پر کردن shift_lookup
                for r in rows:
                    shift_id = str(r['Id_shift'])
                    recorder_id = r['Id_sound_recorder']
                    name = r['SoundRecorderName']

                    if action == 'transfer_previous':
                        prev_date_g = r['Shift_date']  # تاریخ میلادی ماه قبل
                        # اختلاف روز بین ابتدای ماه قبل و تاریخ فعلی
                        day_offset = (prev_date_g - first_prev).days
                        # تاریخ معادل در ماه جاری
                        new_date_g = first_day_g + timedelta(days=day_offset)
                        date_str = new_date_g.strftime('%Y-%m-%d')
                    else:
                        date_str = r['Shift_date'].strftime('%Y-%m-%d')
                        # 🔸 فقط اگر تاریخ داخل ماه فعلی هست
                    if date_str not in valid_dates:
                        continue
                    shift_lookup.setdefault(date_str, {})[shift_id] = {
                        'name': name,
                        'sound_recorder': recorder_id
                    }

                # print(f"✅ Loaded {len(rows)} shifts for action={action}")

        except Exception as e:
            print("❌ SQL Error:", e)
        # print("=== DEBUG KEYS ===")
        # print("shift_lookup keys:", list(shift_lookup.keys())[:5])
        # print("first daily_forms:", [d["greg_date"] for d in daily_forms[:5]])

        # for k, v in list(shift_lookup.items())[:3]:
        #     print(" ", k, "->", list(v.keys()), list(v.values())[:1])

    context = {
        'header_form': header_form,
        'daily_forms': daily_forms,
        'shifts': shifts,
        'shift_lookup': shift_lookup,
        'today': selected_date,
    }
    return render(request, 'main/includes/sound_recorders/current_affairs/create_new/create_new.html', context)
@csrf_exempt
def save_shift_assignments_bulk(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "فقط درخواست POST مجاز است"})

    try:
        data = json.loads(request.body)
        assignments = data.get("assignments", [])
        network_id = data.get("network_id")
        action = data.get("action")  # 'initial' یا 'final'
        user_name = request.user.username if request.user.is_authenticated else "system"

        with connect_db() as conn:
            cursor = conn.cursor()

            for a in assignments:
                shift_date = a["date"]
                # دریافت نام روز (در صورت نیاز می‌توانید locale تنظیم کنید)
                shift_day = pyodbc.Date.fromisoformat(shift_date).strftime('%A')

                # اجرای پروسیجر بر اساس action
                if action == "initial":
                    cursor.execute(
                        "EXEC Sp_InsertSoundShiftAssignment @id_sound_recorder=?, @id_shift=?, @id_network=?, @shift_date=?, @shift_day=?, @user_name=?",
                        (
                            a["sound_recorder_id"],
                            a["shift_id"],
                            network_id,
                            shift_date,
                            shift_day,
                            user_name
                        )

                    )

                elif action == "final":
                    cursor.execute(
                        "EXEC Sp_InsertSoundShiftFinal @id_sound_recorder=?, @id_shift=?, @id_network=?, @shift_date=?, @shift_day=?, @user_name=?",
                        (
                            a["sound_recorder_id"],
                            a["shift_id"],
                            network_id,
                            shift_date,
                            shift_day,
                            user_name
                        )
                    )
                else:
                    return JsonResponse({"status": "error", "message": "عملیات نامعتبر"})

                # ======= بررسی دقیق result set های بازگشتی از SP =======
                rows = None
                result_found = False

                while True:
                    if cursor.description is not None:
                        try:
                            candidate_rows = cursor.fetchall()
                            print("=== DEBUG ROWS ===", candidate_rows)
                        except pyodbc.ProgrammingError:
                            candidate_rows = None

                        if candidate_rows and len(candidate_rows) > 0:
                            first = candidate_rows[0]
                            # اگر ستون اول رشته‌ایه و پیام قابل‌تشخیصه (مثل ⛔ یا تخصیص یا خطا)
                            if isinstance(first[0], str) and (
                                    "⛔" in first[0]
                                    or "تخصیص" in first[0]
                                    or "خطا" in first[0]
                                    or "موفق" in first[0]
                            ):
                                rows = candidate_rows
                                result_found = True
                                break
                    if not cursor.nextset():
                        break

                if result_found and rows and len(rows) > 0:
                    first = rows[0]
                    msg = first[0] if len(first) > 0 else None
                    returned_id = None
                    try:
                        returned_id = int(first[1]) if len(first) > 1 and first[1] is not None else None
                    except (ValueError, TypeError):
                        returned_id = None
                        # اگر ستون سوم (ConflictDate) موجود بود، آن را به Jalali تبدیل کن و پیام را دقیق کن
                        # فیلدهای اختیاری برای خطاهای هم‌پوشانی
                    conflict_date = first[2] if len(first) > 2 else None
                    conflict_shift = first[3] if len(first) > 3 else None
                    conflict_network = first[4] if len(first) > 4 else None

                        # تبدیل تاریخ میلادی به شمسی
                    jalali_display = None
                    if conflict_date:
                        try:
                            greg_date = datetime.strptime(str(conflict_date), "%Y-%m-%d").date()
                            j_date = jdatetime.date.fromgregorian(date=greg_date)
                            jalali_display = f"{j_date.year}/{j_date.month:02}/{j_date.day:02}"
                        except Exception:
                            pass

                    # ساخت پیام نهایی فارسی
                    if returned_id is not None and returned_id < 0:
                        # اگر خطا مربوط به هم‌پوشانی زمانی بود
                        if returned_id == -2:
                            full_message = "⛔ هم‌پوشانی زمانی"
                            if conflict_shift:
                                full_message += f" با  «{conflict_shift}»"
                            if jalali_display:
                                full_message += f" در تاریخ {jalali_display}"
                            if conflict_network:
                                full_message += f" در شبکه «{conflict_network}»"
                            full_message += " وجود دارد."
                            conn.rollback()
                            return JsonResponse({"status": "error", "message": full_message}, status=400)
                        # اگر خطا مربوط به محدودیت 16 ساعته بود
                        # بیش از 16 ساعت
                        elif returned_id == -3:
                            total_minutes = first[2] if len(first) > 2 else None
                            msg = "⛔ مجموع ساعات شیفت‌های این صدابردار در بازهٔ ۲۴ ساعته بیش از ۱۶ ساعت است."
                            if total_minutes:
                                msg += f" (در حال حاضر {total_minutes // 60} ساعت و {total_minutes % 60} دقیقه)"
                            conn.rollback()
                            return JsonResponse({"status": "error", "message": msg}, status=400)

                        # سایر خطاهای احتمالی
                        else:
                            conn.rollback()
                            return JsonResponse({"status": "error", "message": str(msg or "خطا در SP")})
            # ✅ اگر همه بدون خطا انجام شد
            conn.commit()
            return JsonResponse({"status": "success"})

    except pyodbc.Error as e:
        # خطای دیتابیس
        return JsonResponse({"status": "error", "message": f"خطای دیتابیس: {str(e)}"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"خطای غیرمنتظره: {str(e)}"})


