from django.shortcuts import render

from .forms import HeaderForm
from .models import Shift, Network_Shift
from sound_recorders.models import MiddlewareShift
import jdatetime as jd
from datetime import timedelta, datetime
from utils.db_connection import connect_db
from dateutil.relativedelta import relativedelta

def get_shift_group_map():
    """Mapping between real shift id and its group (Base/Join)."""
    shift_map = {}
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Base_shift, Join_shift FROM Tbl_Middleware_Shift")
        rows = cursor.fetchall()
        for r in rows:
            base_shift = str(r[0])
            join_shift = str(r[1]) if r[1] else None
            if join_shift:
                shift_map[join_shift] = base_shift  # Join belongs to Base group
            shift_map[base_shift] = base_shift  # Base maps to itself
    return shift_map

# def get_shift_group_map():
#     with connect_db() as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT Base_shift, Join_shift FROM Tbl_Middleware_Shift")
#         rows = cursor.fetchall()
#
#     # dict:  { real_id: group_id }
#     return {str(r[0]): str(r[1]) for r in rows}

def to_int_or_none(val):
    try:
        return int(val) if val not in (None, '', ' ') else None
    except:
        return None


def to_farsi_numbers(s):
    farsi_digits = "۰۱۲۳۴۵۶۷۸۹"
    return ''.join(farsi_digits[int(c)] if c.isdigit() else c for c in str(s))


def Search_shift(request):
    shift_group_map = get_shift_group_map()
    global selected_sound_recorder, shift_table_choice, template_name
    shift_table_choice = None
    header_form = HeaderForm(request.POST or None)
    selected_network = None
    selected_sound_recorder = None
    selected_date = jd.date.today()

    # ------------------ POST → session ------------------
    if request.method == "POST" and header_form.is_valid():
        # تاریخ
        p_date = header_form.cleaned_data.get("p_date")
        if p_date:
            if isinstance(p_date, jd.date):
                p_date_g = p_date.togregorian()
            else:
                p_date_g = p_date
            # ذخیره به صورت رشته YYYY-MM-DD
            request.session["p_date"] = p_date_g.strftime("%Y-%m-%d")
            selected_date = p_date
        else:
            request.session["p_date"] = None

        # شبکه و صدابردار
        selected_network = header_form.cleaned_data.get("network")
        selected_sound_recorder = header_form.cleaned_data.get("sound_recorder")
        request.session["network"] = to_int_or_none(selected_network.id_network if selected_network else None)
        request.session["sound_recorder"] = to_int_or_none(
            selected_sound_recorder.id_sound_recorder if selected_sound_recorder else None)
        shift_table_choice = request.POST.get("shift_table_choice")

        if shift_table_choice:
            request.session["shift_table_choice"] = shift_table_choice
        action = request.POST.get('action')
        # 🔹 اعتبار انتخاب‌ها
        if ((not selected_network) and (not selected_sound_recorder)) or (selected_network and selected_sound_recorder) or (not shift_table_choice):
            return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html", {
                "header_form": header_form,
                "error_message": "❌جهت بازدید گزارش لطفاً فقط شبکه یا صدابردار را انتخاب کنید و حتما جدول شیفت را تعیین کنید!",
            })

        # 🔹 تعیین تاریخ درست بسته به دکمه
    # ------------------ مقدار session برای GET یا POST ------------------
    if not selected_network and request.session.get("network"):
        selected_network = to_int_or_none(request.session.get("network"))
    if not selected_sound_recorder and request.session.get("sound_recorder"):
        selected_sound_recorder = to_int_or_none(request.session.get("sound_recorder"))

    # تاریخ
    if request.session.get("p_date"):
        year, month, day = map(int, request.session.get("p_date").split("-"))
        selected_date = jd.date.fromgregorian(day=day, month=month, year=year)
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
            'jalali_date': to_farsi_numbers(j_day.strftime("%Y/%m/%d")),
            'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
            'greg_date': g_day.strftime('%Y-%m-%d')
        })

    # اجرای Stored Procedure برای نمایش داده‌ها
    shift_lookup = {}

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            # فرض: selected_network از فرم گرفته شده، خودش ممکنه عدد باشه
            network_id = to_int_or_none(request.session.get("network"))  # اگر None یا '' بود هم None میشه
            recorder_id = to_int_or_none(request.session.get("sound_recorder"))
            if shift_table_choice == '1':
                cursor.execute(
                    "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?, @id_sound_recorder=?",
                    (first_day_g, last_day_g, network_id, recorder_id),
                )
            elif shift_table_choice == '2':
                cursor.execute(
                    "EXEC Sp_ShiftShow_final @start_date=?, @end_date=?, @id_network=?, @id_sound_recorder=?",
                    (first_day_g, last_day_g, network_id, recorder_id),
                )

                # گرفتن خروجی
            cols = [column[0] for column in cursor.description]
            rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
            # 🟦 لیست تاریخ‌های مجاز (روزهای ماه فعلی)
            shift_lookup = {}
            # valid_dates = {d['greg_date'] for d in daily_forms}

            for r in rows:
                date_str = r['Shift_date'].strftime('%Y-%m-%d')  # یا نام فیلد تاریخ شما
                # if date_str not in valid_dates:
                #     continue
                shift_id = str(r['Id_shift'])
                if selected_network:
                # حالت شبکه → فقط اسم صدابردار در سلول
                    shift_lookup.setdefault(date_str, {})[shift_id] = {
                        "name": r.get("SoundRecorderName"),
                        "sound_recorder": r.get("Id_sound_recorder"),
                    }

                elif selected_sound_recorder:

                    # حالت صدابردار → نام شیفت + نام شبکه
                    txt = f"{r['Shift_name']} - {r['Network']}"
                    real_id = str(r["Id_shift"])
                    group_id = shift_group_map.get(real_id)

                    # اگر نبود، بپر بیرون
                    if not group_id:
                        continue

                    shift_list = shift_lookup.setdefault(date_str, {}).setdefault(group_id, [])

                    # append نفر جدید
                    shift_list.append(txt)
                    # shift_lookup.setdefault(date_str, {}).setdefault(shift_id, []).append(txt)
                    # shift_lookup.setdefault(date_str, {}).setdefault(str(r['Id_shift']), []).append(txt)
                    print(shift_lookup)
                # shift_lookup.setdefault(date_str, {})[shift_id] = {
                #     "name": r.get("SoundRecorderName"),
                #     "sound_recorder": r.get("Id_sound_recorder"),
                # }


    except Exception as e:
        print("❌ SQL Error:", e)
        # print("=== DEBUG KEYS ===")
        # print("shift_lookup keys:", list(shift_lookup.keys())[:5])
        # print("first daily_forms:", [d["greg_date"] for d in daily_forms[:5]])

        # for k, v in list(shift_lookup.items())[:3]:
        #     print(" ", k, "->", list(v.keys()), list(v.values())[:1])
    template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"  # پیش‌فرض
    if selected_network:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"
    elif selected_sound_recorder:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_recorder.html"
    else :
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"
    shift_columns = ['1', '2', '3']  # ستون‌های 8 ساعته

    return render(request, template_name, {
        "header_form": header_form,
        "daily_forms": daily_forms,
        "shift_lookup": shift_lookup,
        "shifts": shifts,
        "network": selected_network,
        "sound_recorder": selected_sound_recorder,
        "shift_columns": shift_columns,
    })
    # context = {
    #     'sound_recorder': selected_sound_recorder,
    #     'network': selected_network,
    #     'header_form': header_form,
    #     'daily_forms': daily_forms,
    #     'shifts': shifts,
    #     'shift_lookup': shift_lookup,
    #     'today': selected_date,
    # }
    # return render(request, 'main/includes/sound_recorders/current_affairs/sound_shift_search/test.html', context)


# def Search_shift_recorder(request):
#     header_form = HeaderForm(request.POST or None)
#     selected_sound_recorder = None
#     selected_date = jd.date.today()
#
#     if request.method == "POST" and header_form.is_valid():
#         selected_sound_recorder = header_form.cleaned_data.get("sound_recorder")
#         request.session["sound_recorder"] = to_int_or_none(
#             selected_sound_recorder.id_sound_recorder if selected_sound_recorder else None)
#
#         # تاریخ انتخاب‌شده
#         p_date = header_form.cleaned_data.get("p_date")
#         if p_date:
#             selected_date = p_date
#             request.session["p_date"] = selected_date.strftime("%Y-%m-%d")
#
#     # مقدار session اگر GET بود
#     if not selected_sound_recorder and request.session.get("sound_recorder"):
#         selected_sound_recorder = selected_sound_recorder.objects.filter(
#             id_sound_recorder=request.session.get("sound_recorder")
#         ).first()
#     #
#     # if not selected_sound_recorder:
#     #     return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/test.html", {
#     #         "header_form": header_form,
#     #         "error_message": "❌ لطفاً یک صدابردار انتخاب کنید!"
#     #     })
#
#     # تاریخ‌های ماه جاری
#     year, month = selected_date.year, selected_date.month
#     first_day_j = jd.date(year, month, 1)
#     next_month_j = jd.date(year + 1, 1, 1) if month == 12 else jd.date(year, month + 1, 1)
#     last_day_j = next_month_j - timedelta(days=1)
#     first_day_g = first_day_j.togregorian()
#     last_day_g = last_day_j.togregorian()
#
#     # اجرای Stored Procedure برای دریافت شیفت‌ها
#     shift_lookup = {}
#     try:
#         with connect_db() as conn:
#             cursor = conn.cursor()
#             recorder_id = selected_sound_recorder.id_sound_recorder
#
#             # اجرای SP که شیفت‌های صدابردار را برمی‌گرداند
#             cursor.execute(
#                 "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_sound_recorder=?",
#                 (first_day_g, last_day_g, recorder_id)
#             )
#
#             cols = [c[0] for c in cursor.description]
#             rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
#
#             # آماده‌سازی lookup به شکل:
#             # shift_lookup[date][shift_column] = list of "شبکه + شیفت"
#             for r in rows:
#                 date_str = r['Shift_date'].strftime('%Y-%m-%d')
#                 shift_col = r['Shift_order']  # فرض: ستون 1، 2، 3 برای 3 شیفت 8 ساعته
#                 shift_name = r.get("Shift_name")
#                 network_name = r.get("Network_name")
#
#                 shift_lookup.setdefault(date_str, {}).setdefault(shift_col, []).append(
#                     f"{shift_name} شبکه {network_name}")
#
#     except Exception as e:
#         print("❌ SQL Error:", e)
#
#     # آماده‌سازی روزهای ماه
#     daily_forms = []
#     weekdays_fa = {
#         "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
#         "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
#         "Thursday": "پنجشنبه", "Friday": "جمعه",
#     }
#     for d in range(1, last_day_j.day + 1):
#         j_day = jd.date(year, month, d)
#         g_day = j_day.togregorian()
#         daily_forms.append({
#             'jalali_date': to_farsi_numbers(j_day.strftime("%Y/%m/%d")),
#             'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
#             'greg_date': g_day.strftime('%Y-%m-%d')
#         })
#
#     context = {
#         "header_form": header_form,
#         "sound_recorder": selected_sound_recorder,
#         "daily_forms": daily_forms,
#         "shift_lookup": shift_lookup
#     }
#     return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_recorder.html",
#                   context)

# def Search_shift(request):
#     header_form = HeaderForm(request.POST or None)
#     selected_network = None
#     selected_sound_recorder = None
#     selected_date = jd.date.today()
#
#     # ---------------- POST → session ----------------
#     if request.method == "POST" and header_form.is_valid():
#         # تاریخ
#         p_date = header_form.cleaned_data.get("p_date")
#         if p_date:
#             selected_date = p_date
#             g_date = p_date.togregorian() if isinstance(p_date, jd.date) else p_date
#             request.session["p_date"] = g_date.strftime("%Y-%m-%d")
#         else:
#             request.session["p_date"] = None
#
#         # شبکه و صدابردار
#         selected_network = header_form.cleaned_data.get("network")
#         selected_sound_recorder = header_form.cleaned_data.get("sound_recorder")
#
#         # ذخیره session
#         request.session["network"] = selected_network.id_network if selected_network else None
#         request.session["sound_recorder"] = selected_sound_recorder.id_sound_recorder if selected_sound_recorder else None
#
#         # اعتبارسنجی انتخاب‌ها
#         if (not selected_network and not selected_sound_recorder) or (selected_network and selected_sound_recorder):
#             context = {
#                 "header_form": header_form,
#                 "error_message": "❌ لطفاً فقط شبکه یا فقط صدابردار را انتخاب کنید!"
#             }
#             return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_recorder.html", context)
#
#     else:
#         network_id = request.session.get("network")
#         if network_id:
#             try:
#                 selected_network = Network.objects.get(id_network=network_id)
#             except Network.DoesNotExist:
#                 selected_network = None
#
#         sound_recorder_id = request.session.get("sound_recorder")
#         if sound_recorder_id:
#             try:
#                 selected_sound_recorder = Sound_Recorders.objects.get(id_sound_recorder=sound_recorder_id)
#             except Sound_Recorders.DoesNotExist:
#                 selected_sound_recorder = None
#
#     # تاریخ‌ها برای ماه
#     year, month = selected_date.year, selected_date.month
#     first_day_j = jd.date(year, month, 1)
#     next_month_j = jd.date(year + 1, 1, 1) if month == 12 else jd.date(year, month + 1, 1)
#     last_day_j = next_month_j - timedelta(days=1)
#
#     weekdays_fa = {
#         "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
#         "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
#         "Thursday": "پنجشنبه", "Friday": "جمعه",
#     }
#
#     daily_forms = []
#     for d in range(1, last_day_j.day + 1):
#         j_day = jd.date(year, month, d)
#         g_day = j_day.togregorian()
#         daily_forms.append({
#             "jalali_date": j_day.strftime("%Y/%m/%d"),
#             "jalali_day_name": weekdays_fa[j_day.strftime("%A")],
#             "greg_date": g_day.strftime("%Y-%m-%d")
#         })
#
#     # ---------------- جدول برای شبکه یا صدابردار ----------------
#     table_cells = {}
#     if selected_network:
#         # حالت شبکه: همون لوکاپ قبلی
#         shifts = Network_Shift.objects.filter(id_network=selected_network).select_related("id_shift")
#         shift_lookup = {}
#         for s in shifts:
#             date_str = s.id_shift.start_time.strftime("%Y-%m-%d") if hasattr(s.id_shift, 'start_time') else ''
#             shift_lookup.setdefault(date_str, []).append(s)
#         table_cells = shift_lookup
#
#     elif selected_sound_recorder:
#         # حالت صدابردار: جدول 3 ستون 8 ساعته با تقسیم 4 ساعته
#         assignments = SoundShiftAssignment.objects.filter(
#             id_sound_recorder=selected_sound_recorder,
#             shift_date__gte=first_day_j.togregorian(),
#             shift_date__lte=last_day_j.togregorian()
#         ).select_related("id_network", "id_shift")
#         daily_cells = {}
#         for day in daily_forms:
#             date_str = day["greg_date"]
#             cells = [[], [], []]  # سه ستون
#             day_assignments = [a for a in assignments if a.shift_date.strftime("%Y-%m-%d") == date_str]
#             col_index = 0
#             for a in day_assignments:
#                 hours = (a.id_shift.end_time.hour - a.id_shift.start_time.hour)
#                 if hours == 8:
#                     cells[col_index] = [{"network": a.id_network.network, "full": True}]
#                 elif hours == 4:
#                     if not cells[col_index]:
#                         cells[col_index].append({"network": a.id_network.network, "full": False})
#                     else:
#                         cells[col_index].append({"network": a.id_network.network, "full": False})
#                         col_index += 1 if col_index < 2 else 0
#             for i in range(3):
#                 if not cells[i]:
#                     cells[i] = [None, None]
#             daily_cells[date_str] = cells
#         table_cells = daily_cells
#
#     context = {
#         "header_form": header_form,
#         "daily_forms": daily_forms,
#         "table_cells": table_cells,
#         "selected_network": selected_network,
#         "selected_sound_recorder": selected_sound_recorder
#     }
#     return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_recorder.html", context)
