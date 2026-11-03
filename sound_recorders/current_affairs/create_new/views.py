# import jdatetime
# import pyodbc
# from django.conf import settings
# from django.shortcuts import render
# from django.views.decorators.http import require_POST
# from django.db import connection, DatabaseError
# from .forms import HeaderForm
# from .models import Shift, Network_Shift
# import jdatetime as jd
# from datetime import timedelta, datetime
# import json
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from utils.db_connection import connect_db
# from dateutil.relativedelta import relativedelta
#
# def create_new(request):
#     header_form = HeaderForm(request.POST or None)
#     selected_network = None
#     selected_date = jd.date.today()
#
#     if request.method == "POST" and header_form.is_valid():
#         selected_date = header_form.cleaned_data.get('p_date') or selected_date
#         selected_network = header_form.cleaned_data.get('network')
#         action = request.POST.get('action')
#     # تاریخ‌ها برای ماه انتخاب‌شده
#     year, month = selected_date.year, selected_date.month
#     # تاریخ‌های ماه جاری
#     first_day_j = jd.date(year, month, 1)
#     next_month_j = jd.date(year + 1, 1, 1) if month == 12 else jd.date(year, month + 1, 1)
#     last_day_j = next_month_j - timedelta(days=1)
#     first_day_g = first_day_j.togregorian()
#     last_day_g = last_day_j.togregorian()
#
#     # فقط برای قفل کردن (UPDATE)
#     lock_start_g = first_day_g
#     lock_end_g = next_month_j.togregorian()  # اول ماه بعد
#
#     # تاریخ‌های ماه قبل
#     prev_year = year - 1 if month == 1 else year
#     prev_month = 12 if month == 1 else month - 1
#
#     first_prev_j = jd.date(prev_year, prev_month, 1)
#     last_prev_j = first_day_j - timedelta(days=1)  # آخرین روز ماه قبل دقیقا یک روز قبل از اول ماه جاری است
#
#     first_prev = first_prev_j.togregorian()
#     last_prev = last_prev_j.togregorian()
#
#     # گرفتن شیفت‌های شبکه
#     shifts = []
#     if selected_network:
#         shift_ids = Network_Shift.objects.filter(id_network=selected_network).values_list('id_shift', flat=True)
#         shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by('shift_number')
#
#     weekdays_fa = {
#         "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
#         "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
#         "Thursday": "پنجشنبه", "Friday": "جمعه",
#     }
#     # ساخت جدول روزهای ماه
#
#     daily_forms = []
#     for d in range(1, last_day_j.day + 1):
#         j_day = jd.date(year, month, d)
#         g_day = j_day.togregorian()
#         daily_forms.append({
#             'jalali_date': j_day.strftime('%Y/%m/%d'),
#             'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
#             'greg_date': g_day.strftime('%Y-%m-%d')
#         })
#
#     # اجرای Stored Procedure برای نمایش داده‌ها
#     shift_lookup = {}
#     is_locked = False
#
#     if selected_network:
#         network_id = selected_network.id_network if hasattr(selected_network, 'id_network') else int(selected_network)
#         action = request.POST.get('action')
#         try:
#             with connect_db() as conn:
#                 cursor = conn.cursor()
#                 # 🔹 نمایش جدول ابتدایی
#                 if action == 'current_month':
#                     cursor.execute(
#                         "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?",
#                         (first_day_g, last_day_g, network_id)
#                     )
#                 elif action == 'final_month':
#                     cursor.execute(
#                         "EXEC Sp_ShiftShow_Final @start_date=?, @end_date=?, @id_network=?",
#                         (first_day_g, last_day_g, network_id)
#                     )
#                 elif action == 'transfer_previous':
#                     # ابتدا شیفت‌های ماه قبل
#                     cursor.execute(
#                         "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?",
#                         (first_prev, last_prev, network_id)
#                     )
#                 elif action == 'lock':
#                     cursor.execute(
#                         "EXEC Sp_Lock_Status_Shift ?, ?, ?",
#                         (network_id, lock_start_g, lock_end_g)
#                     )
#                     conn.commit()
#                     is_locked = True
#                     cursor.execute(
#                         "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?",
#                         (first_day_g, last_day_g, network_id))
#
#
#                 if cursor.description:
#                     cols = [column[0] for column in cursor.description]
#                     rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
#                 else:
#                     rows = []
#
#                 with connect_db() as conn:
#                     cursor = conn.cursor()
#                     cursor.execute("""
#                            SELECT TOP 1 1
#                            FROM Tbl_Sound_Shift_Assignment
#                            WHERE Id_network = ?
#                              AND Shift_date BETWEEN ? AND ?
#                              AND Lock = 1
#                        """, (network_id, first_day_g, last_day_g))
#                     # cursor.execute(
#                     #     "EXEC Sp_Select_Lock_Status @start_date=?, @end_date=?, @id_network=?",
#                     #     (first_day_g, last_day_g, network_id))
#                     if cursor.fetchone():
#                         is_locked = True
#
#                 # 🟦 لیست تاریخ‌های مجاز (روزهای ماه فعلی)
#                 valid_dates = {d['greg_date'] for d in daily_forms}
#                 # پر کردن shift_lookup
#                 for r in rows:
#                     shift_id = str(r['Id_shift'])
#                     recorder_id = r['Id_sound_recorder']
#                     name = r['SoundRecorderName']
#
#                     if action == 'transfer_previous':
#                         prev_date_g = r['Shift_date']  # تاریخ میلادی ماه قبل
#                         # اختلاف روز بین ابتدای ماه قبل و تاریخ فعلی
#                         day_offset = (prev_date_g - first_prev).days
#                         # تاریخ معادل در ماه جاری
#                         new_date_g = first_day_g + timedelta(days=day_offset)
#                         date_str = new_date_g.strftime('%Y-%m-%d')
#                     else:
#                         date_str = r['Shift_date'].strftime('%Y-%m-%d')
#                         # 🔸 فقط اگر تاریخ داخل ماه فعلی هست
#                     if date_str not in valid_dates:
#                         continue
#                     shift_lookup.setdefault(date_str, {})[shift_id] = {
#                         'name': name,
#                         'sound_recorder': recorder_id
#                     }
#
#
#         except Exception as e:
#             print("❌ SQL Error:", e)
#
#
#     context = {
#         'header_form': header_form,
#         'daily_forms': daily_forms,
#         'shifts': shifts,
#         'shift_lookup': shift_lookup,
#         'today': selected_date,
#         'is_locked': is_locked,
#     }
#     return render(request, 'main/includes/sound_recorders/current_affairs/create_new/create_new.html', context)
# @csrf_exempt
# def save_shift_assignments_bulk(request):
#     if request.method != "POST":
#         return JsonResponse({"status": "error", "message": "فقط درخواست POST مجاز است"})
#
#     try:
#         data = json.loads(request.body)
#         assignments = data.get("assignments", [])
#         network_id = data.get("network_id")
#         action = data.get("action")  # 'initial' یا 'final'
#         user_name = request.user.username if request.user.is_authenticated else "system"
#         errors = []  # 🔴 جمع‌کننده همه خطاها
#         # print(assignments)
#         with connect_db() as conn:
#             cursor = conn.cursor()
#             for a in assignments:
#                 shift_date = a["date"]
#                 # دریافت نام روز (در صورت نیاز می‌توانید locale تنظیم کنید)
#                 shift_day = pyodbc.Date.fromisoformat(shift_date).strftime('%A')
#                 if action == "initial":
#                     cursor.execute(
#                         "EXEC Sp_InsertSoundShiftAssignment @id_sound_recorder=?, @id_shift=?, @id_network=?, @shift_date=?, @shift_day=?, @user_name=?",
#                         (
#                             a["sound_recorder_id"],
#                             a["shift_id"],
#                             network_id,
#                             shift_date,
#                             shift_day,
#                             user_name
#                         )
#
#                     )
#
#                 elif action == "final":
#                     cursor.execute(
#                         "EXEC Sp_InsertSoundShiftFinal @id_sound_recorder=?, @id_shift=?, @id_network=?, @shift_date=?, @shift_day=?, @user_name=?",
#                         (
#                             a["sound_recorder_id"],
#                             a["shift_id"],
#                             network_id,
#                             shift_date,
#                             shift_day,
#                             user_name
#                         )
#                     )
#                 else:
#                     return JsonResponse({"status": "error", "message": "عملیات نامعتبر"})
#
#                 # ======= بررسی دقیق result set های بازگشتی از SP =======
#                 rows = None
#                 result_found = False
#
#                 while True:
#                     if cursor.description is not None:
#                         try:
#                             candidate_rows = cursor.fetchall()
#                             # print("=== DEBUG ROWS ===", candidate_rows)
#                         except pyodbc.ProgrammingError:
#                             candidate_rows = None
#
#                         if candidate_rows and len(candidate_rows) > 0:
#                             first = candidate_rows[0]
#                             # اگر ستون اول رشته‌ایه و پیام قابل‌تشخیصه (مثل ⛔ یا تخصیص یا خطا)
#                             if isinstance(first[0], str) and (
#                                     "⛔" in first[0]
#                                     or "تخصیص" in first[0]
#                                     or "خطا" in first[0]
#                                     or "موفق" in first[0]
#                             ):
#                                 rows = candidate_rows
#                                 result_found = True
#
#                     if not cursor.nextset():
#                         break
#
#                 if result_found and rows and len(rows) > 0:
#                     first = rows[0]
#                     msg = first[0] if len(first) > 0 else None
#                     returned_id = None
#                     try:
#                         returned_id = int(first[1]) if len(first) > 1 and first[1] is not None else None
#                     except (ValueError, TypeError):
#                         returned_id = None
#                         # اگر ستون سوم (ConflictDate) موجود بود، آن را به Jalali تبدیل کن و پیام را دقیق کن
#                         # فیلدهای اختیاری برای خطاهای هم‌پوشانی
#                     conflict_date = first[2] if len(first) > 2 else None
#                     conflict_shift = first[3] if len(first) > 3 else None
#                     conflict_network = first[4] if len(first) > 4 else None
#
#                         # تبدیل تاریخ میلادی به شمسی
#                     jalali_display = None
#                     if conflict_date:
#                         try:
#                             greg_date = datetime.strptime(str(conflict_date), "%Y-%m-%d").date()
#                             j_date = jdatetime.date.fromgregorian(date=greg_date)
#                             jalali_display = f"{j_date.year}/{j_date.month:02}/{j_date.day:02}"
#                         except Exception:
#                             pass
#
#                     # ساخت پیام نهایی فارسی
#                     if returned_id is not None and returned_id < 0:
#                         # اگر خطا مربوط به هم‌پوشانی زمانی بود
#                         if returned_id == -2:
#                             full_message = "⛔ هم‌پوشانی زمانی"
#                             if conflict_shift:
#                                 full_message += f" با  «{conflict_shift}»"
#                             if jalali_display:
#                                 full_message += f" در تاریخ {jalali_display}"
#                             if conflict_network:
#                                 full_message += f" در شبکه «{conflict_network}»"
#                             full_message += " وجود دارد."
#                             # conn.rollback()
#                             # return JsonResponse({"status": "error", "message": full_message}, status=400)
#                             errors.append(full_message)
#                         # اگر خطا مربوط به محدودیت 16 ساعته بود
#                         # بیش از 16 ساعت
#                         elif returned_id == -3:
#                             total_minutes = first[2] if len(first) > 2 else None
#                             conflict_date = first[3] if len(first) > 3 else None
#                             conflict_shift = first[4] if len(first) > 4 else None
#                             conflict_network = first[5] if len(first) > 5 else None
#
#                             # تبدیل تاریخ میلادی به شمسی
#                             jalali_display = None
#                             if conflict_date:
#                                 try:
#                                     greg_date = datetime.strptime(str(conflict_date), "%Y-%m-%d").date()
#                                     j_date = jdatetime.date.fromgregorian(date=greg_date)
#                                     jalali_display = f"{j_date.year}/{j_date.month:02}/{j_date.day:02}"
#                                 except Exception:
#                                     pass
#
#                             msg = "⛔ مجموع ساعات شیفت‌های این صدابردار در بازهٔ ۲۴ ساعته بیش از ۱۶ ساعت است."
#                             if total_minutes:
#                                 msg += f" (در حال حاضر {total_minutes // 60} ساعت و {total_minutes % 60} دقیقه)***"
#                             if jalali_display:
#                                 msg += f"(تاریخ: {jalali_display})***"
#                             if conflict_shift:
#                                 msg += f"( {conflict_shift})***"
#                             if conflict_network:
#                                 msg += f"(شبکه: {conflict_network})***"
#
#                             errors.append(msg)
#
#
#                         # سایر خطاهای احتمالی
#                         else:
#
#                             errors.append(str(msg or "خطا در SP"))
#             conn.commit()
#             if errors:
#
#                 return JsonResponse({
#                     "status": "partial_success",
#                     "message": "برخی شیفت‌ها ثبت نشدند",
#                     "errors": errors
#                 }, status=207)
#             else:
#                 conn.commit()
#                 return JsonResponse({"status": "success"})
#
#     except pyodbc.Error as e:
#         return JsonResponse({"status": "error", "message": f"خطای دیتابیس: {str(e)}"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": f"خطای غیرمنتظره: {str(e)}"})
#
#
#
#
# def get_network_shifts(request):
#     network_id = request.GET.get('network_id')
#     if not network_id:
#         return JsonResponse({'shifts': []})
#
#     try:
#         network_id = int(network_id)
#         shift_ids = Network_Shift.objects.filter(id_network=network_id).values_list('id_shift', flat=True)
#         shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by('shift_number')
#
#         data = []
#         for s in shifts:
#             # 🔹 استفاده از shift_name به جای ساعت/زمان شیفت
#             # اگر نام فیلد شما چیزی مثل shift_title یا name است، همان را جایگزین کنید
#             name_display = getattr(s, 'shift_name', None) or getattr(s, 'title', str(s))
#
#             data.append({
#                 'id': s.id_shift,
#                 'time': str(name_display)  # این مقدار در dropdown نمایش داده می‌شود
#             })
#
#         return JsonResponse({'shifts': data})
#     except Exception as e:
#         print("❌ Error in get_network_shifts:", e)
#         return JsonResponse({'shifts': [], 'error': str(e)}, status=500)
#
# @csrf_exempt
# def swap_network_assignment(request):
#     if request.method != "POST":
#         return JsonResponse({"status": "error", "message": "فقط درخواست POST مجاز است"})
#
#     try:
#         data = json.loads(request.body)
#         from_sound_recorder_id = data.get("from_sound_recorder_id")
#         to_sound_recorder_id = data.get("to_sound_recorder_id")
#         from_network = data.get("from_network")
#         from_shift = data.get("from_shift")
#         to_network = data.get("to_network")
#         to_shift = data.get("to_shift")
#         raw_shift_date = data.get("shift_date")
#         user_name = request.user.username if request.user.is_authenticated else "system"
#
#         if not raw_shift_date:
#             return JsonResponse(
#                 {"status": "error", "message": "تاریخ انتخاب نشده است."}
#             )
#
#         if not from_sound_recorder_id or not to_sound_recorder_id:
#             return JsonResponse(
#                 {
#                     "status": "error",
#                     "message": "لطفاً هر دو صدابردار را انتخاب کنید.",
#                 }
#             )
#             # 🔹 تبدیل تاریخ شمسی به میلادی جهت استعلام و ثبت در SQL Server
#         try:
#             # تبدیل تمام جداکننده‌ها به اسلش
#             clean_date = raw_shift_date.replace('-', '/').strip()
#             j_year, j_month, j_day = map(int, clean_date.split('/'))
#
#             # تبدیل به تاریخ میلادی
#             g_date = jdatetime.date(j_year, j_month, j_day).togregorian()
#             shift_date = g_date.strftime('%Y-%m-%d')  # خروجی: 2026-06-22
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": f"فرمت تاریخ شمسی نامعتبر است: {str(e)}"})
#         with connection.cursor() as cursor:
#             # فراخوانی Store Procedure
#             sql = """
#                 EXEC Sp_SwapNetworkFinal
#                     @p_FromSoundRecorderId = %s,
#                     @p_ToSoundRecorderId = %s,
#                     @p_FromNetworkId = %s,
#                     @p_FromShiftId = %s,
#                     @p_ToNetworkId = %s,
#                     @p_ToShiftId = %s,
#                     @p_ShiftDate = %s,
#                     @p_UserName = %s
#             """
#             cursor.execute(sql, [
#                 from_sound_recorder_id,
#                 to_sound_recorder_id,
#                 from_network,
#                 from_shift,
#                 to_network,
#                 to_shift,
#                 shift_date,
#                 user_name
#             ])
#
#             row = cursor.fetchone()
#             if not row:
#                 return JsonResponse({"status": "error", "message": "پاسخی از سرور دریافت نشد."})
#             status_code, message = row[0], row[1]
#
#             if status_code == 1:
#                 return JsonResponse({"status": "success", "message": message})
#             else:
#                 return JsonResponse({"status": "error", "message": message})
#
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": f"خطا در اجرای عملیات: {str(e)}"})

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

# from sound_recorders.models import Network_Shift


# def get_shifts_by_network(request):
#     network_id = request.GET.get('network_id')
#     if not network_id:
#         return JsonResponse([], safe=False)
#
#     shifts = Network_Shift.objects.filter(
#         id_network_id=network_id,
#         id_shift__active=True,
#         id_shift__is_active=True,
#         id_shift__del=False
#     ).values('id_shift__id_shift', 'id_shift__shift_name')
#
#     data = [{'id': item['id_shift__id_shift'], 'name': item['id_shift__shift_name']} for item in shifts]
#     return JsonResponse(data, safe=False)
#
#
# import json
# from django.http import JsonResponse
#
#
# def swap_network_shifts(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             from_network = data.get('from_network')
#             from_shift = data.get('from_shift')
#             to_network = data.get('to_network')
#             to_shift = data.get('to_shift')
#             p_date = data.get('date')
#
#             # منطق جابجایی دیتابیس را اینجا بنویسید...
#
#             return JsonResponse({'status': 'success', 'message': 'جابجایی شبکه با موفقیت انجام شد.'})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
#
#     return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر است.'}, status=400)


def create_new(request):
    header_form = HeaderForm(request.POST or None)
    selected_network = None
    selected_date = jd.date.today()
    action = None

    if request.method == "POST" and header_form.is_valid():
        selected_date = (
            header_form.cleaned_data.get("p_date")
            or selected_date
        )
        selected_network = header_form.cleaned_data.get("network")
        action = request.POST.get("action")

    # --------------------------------------------------
    # 1. محاسبه تاریخ‌های ماه شمسی انتخاب‌شده
    # --------------------------------------------------
    year, month = selected_date.year, selected_date.month

    first_day_j = jd.date(year, month, 1)
    next_month_j = (
        jd.date(year + 1, 1, 1)
        if month == 12
        else jd.date(year, month + 1, 1)
    )
    last_day_j = next_month_j - timedelta(days=1)

    first_day_g = first_day_j.togregorian()
    last_day_g = last_day_j.togregorian()

    # بازه قفل
    lock_start_g = first_day_g
    lock_end_g = next_month_j.togregorian()

    # --------------------------------------------------
    # 2. تاریخ‌های دقیق ماه شمسی قبل
    # --------------------------------------------------
    prev_year = year - 1 if month == 1 else year
    prev_month = 12 if month == 1 else month - 1

    first_prev_j = jd.date(prev_year, prev_month, 1)
    last_prev_j = first_day_j - timedelta(days=1)

    first_prev = first_prev_j.togregorian()
    last_prev = last_prev_j.togregorian()

    # --------------------------------------------------
    # 3. شیفت‌های متعلق به شبکه
    # --------------------------------------------------
    shifts = []

    if selected_network:
        shift_ids = Network_Shift.objects.filter(
            id_network=selected_network
        ).values_list("id_shift", flat=True)

        shifts = Shift.objects.filter(
            id_shift__in=shift_ids
        ).order_by("shift_number")

    # --------------------------------------------------
    # 4. ساخت روزهای جدول ماه جدید
    # --------------------------------------------------
    weekdays_fa = {
        "Saturday": "شنبه",
        "Sunday": "یکشنبه",
        "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه",
        "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه",
        "Friday": "جمعه",
    }

    daily_forms = []

    for d in range(1, last_day_j.day + 1):
        j_day = jd.date(year, month, d)
        g_day = j_day.togregorian()

        daily_forms.append({
            "jalali_date": j_day.strftime("%Y/%m/%d"),
            "jalali_day_name": weekdays_fa[j_day.strftime("%A")],
            "greg_date": g_day.strftime("%Y-%m-%d"),
        })

    # --------------------------------------------------
    # 5. دریافت اطلاعات متناسب با دکمه انتخاب‌شده
    # --------------------------------------------------
    shift_lookup = {}
    is_locked = False
    rows = []

    if selected_network:
        network_id = (
            selected_network.id_network
            if hasattr(selected_network, "id_network")
            else int(selected_network)
        )

        try:
            with connect_db() as conn:
                cursor = conn.cursor()

                if action == "current_month":
                    cursor.execute(
                        """
                        EXEC Sp_ShiftShow
                            @start_date=?,
                            @end_date=?,
                            @id_network=?
                        """,
                        (first_day_g, last_day_g, network_id),
                    )

                elif action == "final_month":
                    cursor.execute(
                        """
                        EXEC Sp_ShiftShow_Final
                            @start_date=?,
                            @end_date=?,
                            @id_network=?
                        """,
                        (first_day_g, last_day_g, network_id),
                    )

                elif action == "transfer_previous":

                    cursor.execute(
                        """
                        EXEC dbo.Sp_GetPreviousMonthAssignments
                            @start_date=?,
                            @end_date=?,
                            @previous_start_date=?,
                            @previous_end_date=?,
                            @id_network=?
                        """,
                        (
                            first_day_g,
                            last_day_g,
                            first_prev,
                            last_prev,
                            network_id,
                        ),
                    )

                elif action == "lock":
                    cursor.execute(
                        """
                        EXEC Sp_Lock_Status_Shift ?, ?, ?
                        """,
                        (network_id, lock_start_g, lock_end_g),
                    )
                    conn.commit()
                    is_locked = True

                    cursor.execute(
                        """
                        EXEC Sp_ShiftShow
                            @start_date=?,
                            @end_date=?,
                            @id_network=?
                        """,
                        (first_day_g, last_day_g, network_id),
                    )

                # نتیجه هر استور فقط یک بار خوانده می‌شود
                if cursor.description:
                    columns = [
                        column[0] for column in cursor.description
                    ]
                    rows = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

                # بررسی قفل بودن ماه جدید
                with connect_db() as lock_conn:
                    lock_cursor = lock_conn.cursor()

                    lock_cursor.execute(
                        """
                        SELECT TOP 1 1
                        FROM Tbl_Sound_Shift_Assignment
                        WHERE Id_network = ?
                          AND Shift_date >= ?
                          AND Shift_date < ?
                          AND Lock = 1
                        """,
                        (
                            network_id,
                            first_day_g,
                            next_month_j.togregorian(),
                        ),
                    )

                    if lock_cursor.fetchone():
                        is_locked = True

                # ------------------------------------------
                # 6. قرار دادن اطلاعات در جدول صفحه
                # ------------------------------------------
                valid_dates = {
                    item["greg_date"] for item in daily_forms
                }

                for r in rows:
                    shift_id = str(r["Id_shift"])
                    recorder_id = r["Id_sound_recorder"]
                    name = r.get("SoundRecorderName")
                    shift_date = r["Shift_date"]

                    if hasattr(shift_date, "strftime"):
                        date_str = shift_date.strftime("%Y-%m-%d")
                    else:
                        date_str = str(shift_date)[:10]

                    if date_str not in valid_dates:
                        continue

                    # اگر در ماه قبل صدابرداری برای این
                    # شیفت متناظر وجود نداشته، سلول خالی بماند.
                    if recorder_id is None:
                        continue

                    shift_lookup.setdefault(
                        date_str, {}
                    )[shift_id] = {
                        "name": name or "",
                        "sound_recorder": recorder_id,
                    }

                print("SHIFT LOOKUP DATES:", len(shift_lookup))

        except Exception as e:
            print("SQL Error:", repr(e))

    context = {
        "header_form": header_form,
        "daily_forms": daily_forms,
        "shifts": shifts,
        "shift_lookup": shift_lookup,
        "today": selected_date,
        "is_locked": is_locked,
    }

    return render(
        request,
        "main/includes/sound_recorders/current_affairs/create_new/create_new.html",
        context,
    )

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
        errors = []  # 🔴 جمع‌کننده همه خطاها
        # print(assignments)
        with connect_db() as conn:
            cursor = conn.cursor()
            for a in assignments:
                shift_date = a["date"]
                # دریافت نام روز (در صورت نیاز می‌توانید locale تنظیم کنید)
                shift_day = pyodbc.Date.fromisoformat(shift_date).strftime('%A')
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
                            # print("=== DEBUG ROWS ===", candidate_rows)
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
                            # conn.rollback()
                            # return JsonResponse({"status": "error", "message": full_message}, status=400)
                            errors.append(full_message)
                        # اگر خطا مربوط به محدودیت 16 ساعته بود
                        # بیش از 16 ساعت
                        elif returned_id == -3:
                            total_minutes = first[2] if len(first) > 2 else None
                            conflict_date = first[3] if len(first) > 3 else None
                            conflict_shift = first[4] if len(first) > 4 else None
                            conflict_network = first[5] if len(first) > 5 else None

                            # تبدیل تاریخ میلادی به شمسی
                            jalali_display = None
                            if conflict_date:
                                try:
                                    greg_date = datetime.strptime(str(conflict_date), "%Y-%m-%d").date()
                                    j_date = jdatetime.date.fromgregorian(date=greg_date)
                                    jalali_display = f"{j_date.year}/{j_date.month:02}/{j_date.day:02}"
                                except Exception:
                                    pass

                            msg = "⛔ مجموع ساعات شیفت‌های این صدابردار بیش از ۱۶ ساعت پیوسته می باشد."
                            if total_minutes:
                                # msg += f" (در حال حاضر {total_minutes // 60} ساعت و {total_minutes % 60} دقیقه)***"
                                msg += f""
                            if jalali_display:
                                msg += f"(تاریخ: {jalali_display})***"
                            if conflict_shift:
                                msg += f"( {conflict_shift})***"
                            if conflict_network:
                                msg += f"(شبکه: {conflict_network})***"
                            #
                            # conn.rollback()
                            # return JsonResponse({"status": "error", "message": msg}, status=400)
                            errors.append(msg)


                        # سایر خطاهای احتمالی
                        else:
                            # conn.rollback()
                            # return JsonResponse({"status": "error", "message": str(msg or "خطا در SP")})
                            errors.append(str(msg or "خطا در SP"))
            conn.commit()
            if errors:
                # conn.rollback()
                # return JsonResponse({"status": "error", "errors": errors}, status=400)
                return JsonResponse({
                    "status": "partial_success",
                    "message": "برخی شیفت‌ها ثبت نشدند",
                    "errors": errors
                }, status=207)
            else:
                conn.commit()
                return JsonResponse({"status": "success"})

    except pyodbc.Error as e:
        return JsonResponse({"status": "error", "message": f"خطای دیتابیس: {str(e)}"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"خطای غیرمنتظره: {str(e)}"})

def get_network_shifts(request):
    network_id = request.GET.get('network_id')
    if not network_id:
        return JsonResponse({'shifts': []})

    try:
        network_id = int(network_id)
        shift_ids = Network_Shift.objects.filter(id_network=network_id).values_list('id_shift', flat=True)
        shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by('shift_number')

        data = []
        for s in shifts:
            # 🔹 استفاده از shift_name به جای ساعت/زمان شیفت
            # اگر نام فیلد شما چیزی مثل shift_title یا name است، همان را جایگزین کنید
            name_display = getattr(s, 'shift_name', None) or getattr(s, 'title', str(s))

            data.append({
                'id': s.id_shift,
                'time': str(name_display)  # این مقدار در dropdown نمایش داده می‌شود
            })

        return JsonResponse({'shifts': data})
    except Exception as e:
        print("❌ Error in get_network_shifts:", e)
        return JsonResponse({'shifts': [], 'error': str(e)}, status=500)

@require_POST
def swap_network_assignment(request):
    """
    جابه‌جایی صدابردارهای دو شیفت در جدول اولیه یا نهایی.
    شناسه صدابردارها از خود جدول انتخاب‌شده خوانده می‌شود، نه از مرورگر.
    """
    try:
        data = json.loads(request.body or "{}")
        action = data.get("action")
        if action not in ("initial", "final"):
            return JsonResponse({
                "status": "error",
                "message": "نوع جابه‌جایی نامعتبر است."
            }, status=400)

        try:
            from_network = int(data.get("from_network"))
            from_shift = int(data.get("from_shift"))
            to_network = int(data.get("to_network"))
            to_shift = int(data.get("to_shift"))
        except (TypeError, ValueError):
            return JsonResponse({
                "status": "error",
                "message": "شبکه و شیفت مبدأ و مقصد را به‌درستی انتخاب کنید."
            }, status=400)

        if (from_network, from_shift) == (to_network, to_shift):
            return JsonResponse({
                "status": "error",
                "message": "شبکه و شیفت مبدأ و مقصد نمی‌توانند یکسان باشند."
            }, status=400)

        raw_shift_date = (data.get("shift_date") or "").strip()
        if not raw_shift_date:
            return JsonResponse({
                "status": "error",
                "message": "تاریخ جابه‌جایی انتخاب نشده است."
            }, status=400)

        try:
            clean_date = raw_shift_date.replace("-", "/")
            j_year, j_month, j_day = map(int, clean_date.split("/"))
            shift_date = jdatetime.date(j_year, j_month, j_day).togregorian()
        except (TypeError, ValueError):
            return JsonResponse({
                "status": "error",
                "message": "فرمت تاریخ شمسی معتبر نیست."
            }, status=400)

        table_name, procedure_name = (
            ("Tbl_Sound_Shift_Assignment", "Sp_SwapNetworkAssignment")
            if action == "initial"
            else ("Tbl_Sound_Shift_Final", "Sp_SwapNetworkFinal")
        )
        user_name = (
            request.user.username
            if request.user.is_authenticated
            else "system"
        )

        # بررسی و خواندن صدابردارها از همان جدولی که قرار است تغییر کند.
        # قفل تراکنشی مانع تغییر هم‌زمان رکوردها در فاصله خواندن تا اجرای SP می‌شود.
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT Id_sound_recorder
                FROM dbo.{table_name}
                WHERE Id_network = %s
                  AND Id_shift = %s
                  AND Shift_date = %s
                  AND Active = 1
                  AND Del = 0
            """, [from_network, from_shift, shift_date])
            from_rows = cursor.fetchall()

            cursor.execute(f"""
                SELECT Id_sound_recorder
                FROM dbo.{table_name}
                WHERE Id_network = %s
                  AND Id_shift = %s
                  AND Shift_date = %s
                  AND Active = 1
                  AND Del = 0
            """, [to_network, to_shift, shift_date])
            to_rows = cursor.fetchall()

            if len(from_rows) != 1 or len(to_rows) != 1:
                return JsonResponse({
                    "status": "error",
                    "message": (
                        "برای هر دو شیفت باید دقیقاً یک رکورد فعال وجود داشته باشد. "
                        "هیچ تغییری انجام نشد."
                    )
                }, status=400)

            from_recorder_id = from_rows[0][0]
            to_recorder_id = to_rows[0][0]

            if from_recorder_id == to_recorder_id:
                return JsonResponse({
                    "status": "error",
                    "message": "صدابردار هر دو شیفت یکسان است؛ جابه‌جایی لازم نیست."
                }, status=400)

            # SP علاوه بر انجام UPDATE، شناسه‌های مورد انتظار را نیز کنترل می‌کند.
            cursor.execute(f"""
                EXEC dbo.{procedure_name}
                    @p_FromSoundRecorderId = %s,
                    @p_ToSoundRecorderId = %s,
                    @p_FromNetworkId = %s,
                    @p_FromShiftId = %s,
                    @p_ToNetworkId = %s,
                    @p_ToShiftId = %s,
                    @p_ShiftDate = %s,
                    @p_UserName = %s
            """, [
                from_recorder_id,
                to_recorder_id,
                from_network,
                from_shift,
                to_network,
                to_shift,
                shift_date,
                user_name
            ])

            result = cursor.fetchone()
            if not result:
                raise DatabaseError("Stored Procedure هیچ نتیجه‌ای برنگرداند.")

            status_code, message = result[0], result[1]
            if status_code != 1:
                raise DatabaseError(str(message))

        return JsonResponse({
            "status": "success",
            "message": message
        })

    except DatabaseError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"خطا در اجرای جابه‌جایی: {str(e)}"
        }, status=500)
