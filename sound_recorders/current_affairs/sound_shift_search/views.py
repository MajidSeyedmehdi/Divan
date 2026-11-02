from django.shortcuts import render
from .forms import HeaderForm
from .models import Shift, Network_Shift, SelectSoundRecorder, SelectNetwork
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
        for base, join in cursor.fetchall():
            base = str(base)
            if join:
                shift_map[str(join)] = base
            shift_map[base] = base
    return shift_map


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
    header_form = HeaderForm(request.POST or None)
    selected_network = None
    selected_sound = None

    # ---------------- POST: ذخیره ورودی فرم در session ----------------
    if request.method == "POST" and header_form.is_valid():
        request.session["report_type"] = "month"

        p_date = header_form.cleaned_data.get("p_date")
        if isinstance(p_date, jd.date):
            request.session["p_date"] = p_date.togregorian().strftime("%Y-%m-%d")

        # شبکه
        net_val = header_form.cleaned_data.get("network")  #net_val مقدار انتخاب شده از دراپ دان به رشته تبدیل میشود
        if net_val == HeaderForm.ALL_NETWORK:
            request.session["network"] = "all"    #اگر همه را انتخاب کرد
        elif net_val and net_val.isdigit():
            request.session["network"] = int(net_val)       # اگر همه نبود یعنی یه شبکه خاص با id شبکه رو انتخاب کرد
        else:
            request.session["network"] = None

        # صدابردار
        rec_val = header_form.cleaned_data.get("sound_recorder")
        if rec_val == HeaderForm.ALL_RECORDER:
            request.session["sound_recorder"] = "all_rec"
        elif rec_val and rec_val.isdigit():
            request.session["sound_recorder"] = int(rec_val)
        else:
            request.session["sound_recorder"] = None

        # جدول شیفت
        request.session["shift_table_choice"] = header_form.cleaned_data.get("shift_table_choice")

    # ---------------- GET یا POST → تبدیل session به متغیر ----------------
    selected_date = jd.date.today()

    if request.session.get("p_date"):
        y, m, d = map(int, request.session["p_date"].split("-"))
        selected_date = jd.date.fromgregorian(year=y, month=m, day=d)

    raw_network = request.session.get("network")
    if raw_network == "all":
        selected_network = "all"
    else:
        selected_network = to_int_or_none(raw_network)

    raw_recorder = request.session.get("sound_recorder")
    if raw_recorder == "all_rec":
        selected_sound = "all_rec"
    else:
        selected_sound = to_int_or_none(raw_recorder)

    shift_table_choice = request.session.get("shift_table_choice")

    # ---------------- شرط اعتبار ----------------
    # شبکه خاص انتخاب شده؟
    network_selected = isinstance(selected_network, int)

    # صدابردار خاص انتخاب شده؟
    recorder_selected = isinstance(selected_sound, int)

    # اگر هیچکدام انتخاب نشده‌اند
    if not network_selected and not recorder_selected and \
            selected_network != "all" and selected_sound != "all_rec":
        return render(request,
                      "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html",
                      {
                          "header_form": header_form,
                          "error_message": "❌ لطفاً شبکه یا صدابردار را انتخاب کنید!",
                      })

    # اگر هر دو انتخاب شده‌اند
    if (network_selected or selected_network == "all") and \
            (recorder_selected or selected_sound == "all_rec"):
        return render(request,
                      "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html",
                      {
                          "header_form": header_form,
                          "error_message": "❌ فقط یکی از شبکه یا صدابردار باید انتخاب شود.",
                      })

    # انتخاب جدول
    if not shift_table_choice:
        return render(request,
                      "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html",
                      {
                          "header_form": header_form,
                          "error_message": "❌ لطفاً جدول شیفت را انتخاب کنید.",
                      })

    # ---------------- تاریخ‌های ماه ----------------
    year, month = selected_date.year, selected_date.month
    first_day_j = jd.date(year, month, 1)
    next_month_j = jd.date(year + 1, 1, 1) if month == 12 else jd.date(year, month + 1, 1)
    last_day_j = next_month_j - timedelta(days=1)
    first_day_g = first_day_j.togregorian()
    last_day_g = last_day_j.togregorian()

    # ---------------- لیست روزهای ماه ----------------
    weekdays_fa = {
        "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه", "Friday": "جمعه",
    }

    daily_forms = []
    for d in range(1, last_day_j.day + 1):
        j_day = jd.date(year, month, d)
        g_day = j_day.togregorian()
        daily_forms.append({
            'jalali_date': to_farsi_numbers(j_day.strftime("%Y/%m/%d")),
            'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
            'greg_date': g_day.strftime('%Y-%m-%d')
        })

    # ---------------- دریافت شیفت‌های شبکه ----------------
    shifts = []
    if selected_network and selected_network != "all":
        shift_ids = Network_Shift.objects.filter(id_network=selected_network).values_list('id_shift', flat=True)
        shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by('shift_number')

    # ---------------- اجرای Stored Procedure ----------------
    shift_lookup = {}
    net_lookup = {}  # ← برای حالت ALL اضافه شد، بدون حذف کدهای قبلی

    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            network_id = None if selected_network == "all" else selected_network
            recorder_id = None if selected_sound == "all_rec" else selected_sound

            if shift_table_choice == '1':
                cursor.execute(
                    "EXEC Sp_ShiftShow @start_date=?, @end_date=?, @id_network=?, @id_sound_recorder=?",
                    (first_day_g, last_day_g, network_id, recorder_id)
                )
            else:
                cursor.execute(
                    "EXEC Sp_ShiftShow_final @start_date=?, @end_date=?, @id_network=?, @id_sound_recorder=?",
                    (first_day_g, last_day_g, network_id, recorder_id)
                )

            cols = [c[0] for c in cursor.description]
            rows = [dict(zip(cols, row)) for row in cursor.fetchall()]

            total_shifts = 0
            if cursor.nextset():  # رفتن به result set بعدی
                stat = cursor.fetchone()
                if stat:
                    total_shifts = stat[0]

            for r in rows:
                shift_date = r['Shift_date']
                # فقط تاریخ‌های داخل ماه انتخاب‌شده
                if not (first_day_g <= shift_date <= last_day_g):
                    continue

                date_str = shift_date.strftime('%Y-%m-%d')
                shift_id = str(r['Id_shift'])
                network_name = r.get("Network")

                # ---------------- حالت ALL شبکه------------
                if selected_network == "all":
                    net_lookup.setdefault(network_name, {}).setdefault(date_str, {})[int(shift_id)] = r.get(
                        "SoundRecorderName")

                    continue


                # ---------------- حالت ALL صدابردار------------
                if selected_sound == "all_rec":
                    person = r.get("SoundRecorderName")

                    real_id = str(r["Id_shift"])
                    group_id = shift_group_map.get(real_id)  # مثلاً '1'، '2'، '3'

                    if not group_id:
                        continue

                    txt = r.get("Network")  # چیزی که می‌خواهی داخل سلول نشان بدهی

                    cell_list = (
                        net_lookup
                        .setdefault(person, {})
                        .setdefault(date_str, {})
                        .setdefault(group_id, [])
                    )

                    if txt not in cell_list:
                        cell_list.append(txt)

                    continue

                # ---------------- حالت شبکه خاص ----------------
                if isinstance(selected_network, int) and not selected_sound:
                    shift_lookup.setdefault(date_str, {})[shift_id] = {
                        "name": r.get("SoundRecorderName"),
                        "sound_recorder": r.get("Id_sound_recorder"),
                    }
                    continue

                # ---------------- حالت صدابردار ----------------
                elif selected_sound and not selected_network:
                    txt = f" {network_name}"

                    real_id = str(r["Id_shift"])
                    group_id = shift_group_map.get(real_id)  # ← تبدیل ID واقعی به شماره شیفت (۱،۲،۳)

                    if not group_id:
                        continue

                    shift_lookup.setdefault(date_str, {}).setdefault(group_id, []).append(txt)
                    continue



    except Exception as e:
        print("❌ SQL Error:", e)

        # --------------------------------------------------------------------
    shifts_by_network = {}

    if selected_network == "all":
        for net_name in net_lookup.keys():
            shift_ids = Network_Shift.objects.filter(
                id_network__network=net_name
            ).values_list("id_shift", flat=True)

            net_shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by(
                "shift_number"
            )

            shifts_by_network[net_name] = list(net_shifts)

    # ------------------ همه صدابردارها ------------------
    if selected_sound == "all_rec":
        # همه شیفت‌های موجود در سیستم (1، 2، 3)
        all_shifts = Shift.objects.all().order_by("shift_number")

        for rec_name in net_lookup.keys():
            shifts_by_network[rec_name] = all_shifts

    shift_columns = ['1', '2', '3']

    sound_recorder_name = None

    if isinstance(selected_sound, int):
        try:
            sound_recorder_name = SelectSoundRecorder.objects.get(
                id_sound_recorder=selected_sound
            )
        except SelectSoundRecorder.DoesNotExist:
            sound_recorder_name = None

    network_obj = None

    if isinstance(selected_network, int):
        try:
            network_obj = SelectNetwork.objects.get(
                id_network=selected_network
            )
        except SelectNetwork.DoesNotExist:
            network_obj = None

    # ---------------- انتخاب قالب ----------------


    if selected_network == "all":
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_all.html"

    elif selected_sound == "all_rec":
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_all_recorders.html"

    elif selected_network and not selected_sound:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"

    elif selected_sound and not selected_network:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_recorder.html"

    else:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"

    return render(request, template_name, {
        "header_form": header_form,
        "daily_forms": daily_forms,
        "shift_lookup": shift_lookup,
        "shifts": shifts,
        "network": selected_network,
        "sound_recorder": sound_recorder_name,
        "network_obj": network_obj,
        "shift_columns": shift_columns,
        "net_lookup": net_lookup,
        "shifts_by_network": shifts_by_network,
        "total_shifts": total_shifts,
    })


def Search_shift_weekly(request):
    """ویوی اختصاصی برای گزارش هفتگی (از اولین شنبه ماه تا اولین جمعه)"""
    shift_group_map = get_shift_group_map()
    header_form = HeaderForm(request.POST or None)
    selected_network = None
    selected_sound = None

    # ---------------- POST: ذخیره ورودی فرم در session ----------------
    if request.method == "POST" and header_form.is_valid():
        request.session["report_type"] = "weekly"

        p_date = header_form.cleaned_data.get("p_date")
        if isinstance(p_date, jd.date):
            request.session["p_date"] = p_date.togregorian().strftime("%Y-%m-%d")

        net_val = header_form.cleaned_data.get("network")
        if net_val == HeaderForm.ALL_NETWORK:
            request.session["network"] = "all"
        elif net_val and net_val.isdigit():
            request.session["network"] = int(net_val)
        else:
            request.session["network"] = None

        rec_val = header_form.cleaned_data.get("sound_recorder")
        if rec_val == HeaderForm.ALL_RECORDER:
            request.session["sound_recorder"] = "all_rec"
        elif rec_val and rec_val.isdigit():
            request.session["sound_recorder"] = int(rec_val)
        else:
            request.session["sound_recorder"] = None

        request.session["shift_table_choice"] = header_form.cleaned_data.get("shift_table_choice")

    # ---------------- دریافت تاریخ از session ----------------
    selected_date = jd.date.today()
    if request.session.get("p_date"):
        y, m, d = map(int, request.session["p_date"].split("-"))
        selected_date = jd.date.fromgregorian(year=y, month=m, day=d)

    raw_network = request.session.get("network")
    selected_network = "all" if raw_network == "all" else to_int_or_none(raw_network)

    raw_recorder = request.session.get("sound_recorder")
    selected_sound = "all_rec" if raw_recorder == "all_rec" else to_int_or_none(raw_recorder)

    shift_table_choice = request.session.get("shift_table_choice")

    # ---------------- اعتبارسنجی‌ها ----------------
    network_selected = isinstance(selected_network, int)
    recorder_selected = isinstance(selected_sound, int)

    if not network_selected and not recorder_selected and selected_network != "all" and selected_sound != "all_rec":
        return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html", {
            "header_form": header_form,
            "error_message": "❌ لطفاً شبکه یا صدابردار را انتخاب کنید!",
        })

    if (network_selected or selected_network == "all") and (recorder_selected or selected_sound == "all_rec"):
        return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html", {
            "header_form": header_form,
            "error_message": "❌ فقط یکی از شبکه یا صدابردار باید انتخاب شود.",
        })

    if not shift_table_choice:
        return render(request, "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html", {
            "header_form": header_form,
            "error_message": "❌ لطفاً جدول شیفت را انتخاب کنید.",
        })

    # ---------------- محاسبه بازه اولین شنبه تا اولین جمعه ماه ----------------
    year, month = selected_date.year, selected_date.month
    first_day_j = jd.date(year, month, 1)

    # پیدا کردن اولین شنبه ماه (در jdatetime شنبه index=0 است)
    days_until_saturday = (0 - first_day_j.weekday()) % 7
    first_saturday_j = first_day_j + timedelta(days=days_until_saturday)
    first_friday_j = first_saturday_j + timedelta(days=6)  # ۶ روز بعد از شنبه = جمعه

    first_day_g = first_saturday_j.togregorian()
    last_day_g = first_friday_j.togregorian()

    # ---------------- لیست ۷ روز هفته ----------------
    weekdays_fa = {
        "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه", "Friday": "جمعه",
    }

    daily_forms = []
    for offset in range(7):
        j_day = first_saturday_j + timedelta(days=offset)
        g_day = j_day.togregorian()
        daily_forms.append({
            'jalali_date': to_farsi_numbers(j_day.strftime("%Y/%m/%d")),
            'jalali_day_name': weekdays_fa[j_day.strftime('%A')],
            'greg_date': g_day.strftime('%Y-%m-%d')
        })

    # ---------------- دریافت شیفت‌های شبکه ----------------
    shifts = []
    if selected_network and selected_network != "all":
        shift_ids = Network_Shift.objects.filter(id_network=selected_network).values_list('id_shift', flat=True)
        shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by('shift_number')

    # ---------------- اجرای Stored Procedure ----------------
    shift_lookup = {}
    net_lookup = {}

    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            network_id = None if selected_network == "all" else selected_network
            recorder_id = None if selected_sound == "all_rec" else selected_sound

            sp_name = "Sp_ShiftShow" if shift_table_choice == '1' else "Sp_ShiftShow_final"
            cursor.execute(
                f"EXEC {sp_name} @start_date=?, @end_date=?, @id_network=?, @id_sound_recorder=?",
                (first_day_g, last_day_g, network_id, recorder_id)
            )

            cols = [c[0] for c in cursor.description]
            rows = [dict(zip(cols, row)) for row in cursor.fetchall()]

            total_shifts = 0
            if cursor.nextset():
                stat = cursor.fetchone()
                if stat:
                    total_shifts = stat[0]

            for r in rows:
                shift_date = r['Shift_date']
                if not (first_day_g <= shift_date <= last_day_g):
                    continue

                date_str = shift_date.strftime('%Y-%m-%d')
                shift_id = str(r['Id_shift'])
                network_name = r.get("Network")

                if selected_network == "all":
                    net_lookup.setdefault(network_name, {}).setdefault(date_str, {})[int(shift_id)] = r.get("SoundRecorderName")
                    continue

                if selected_sound == "all_rec":
                    person = r.get("SoundRecorderName")
                    real_id = str(r["Id_shift"])
                    group_id = shift_group_map.get(real_id)
                    if not group_id:
                        continue
                    txt = r.get("Network")
                    cell_list = net_lookup.setdefault(person, {}).setdefault(date_str, {}).setdefault(group_id, [])
                    if txt not in cell_list:
                        cell_list.append(txt)
                    continue

                if isinstance(selected_network, int) and not selected_sound:
                    shift_lookup.setdefault(date_str, {})[shift_id] = {
                        "name": r.get("SoundRecorderName"),
                        "sound_recorder": r.get("Id_sound_recorder"),
                    }
                    continue

                elif selected_sound and not selected_network:
                    txt = f" {network_name}"
                    real_id = str(r["Id_shift"])
                    group_id = shift_group_map.get(real_id)
                    if not group_id:
                        continue
                    shift_lookup.setdefault(date_str, {}).setdefault(group_id, []).append(txt)
                    continue

    except Exception as e:
        print("❌ SQL Error:", e)

    # ---------------- ساخت دکشنری شیفت‌ها ----------------
    shifts_by_network = {}
    if selected_network == "all":
        for net_name in net_lookup.keys():
            shift_ids = Network_Shift.objects.filter(id_network__network=net_name).values_list("id_shift", flat=True)
            net_shifts = Shift.objects.filter(id_shift__in=shift_ids).order_by("shift_number")
            shifts_by_network[net_name] = list(net_shifts)

    if selected_sound == "all_rec":
        all_shifts = Shift.objects.all().order_by("shift_number")
        for rec_name in net_lookup.keys():
            shifts_by_network[rec_name] = all_shifts

    shift_columns = ['1', '2', '3']

    sound_recorder_name = None
    if isinstance(selected_sound, int):
        try:
            sound_recorder_name = SelectSoundRecorder.objects.get(id_sound_recorder=selected_sound)
        except SelectSoundRecorder.DoesNotExist:
            sound_recorder_name = None

    network_obj = None
    if isinstance(selected_network, int):
        try:
            network_obj = SelectNetwork.objects.get(id_network=selected_network)
        except SelectNetwork.DoesNotExist:
            network_obj = None

    # ---------------- انتخاب قالب ----------------
    if selected_network == "all":
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_all.html"
    elif selected_sound == "all_rec":
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_all_recorders.html"
    elif selected_network and not selected_sound:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"
    elif selected_sound and not selected_network:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_recorder.html"
    else:
        template_name = "main/includes/sound_recorders/current_affairs/sound_shift_search/sound_shift_network.html"

    return render(request, template_name, {
        "header_form": header_form,
        "daily_forms": daily_forms,
        "shift_lookup": shift_lookup,
        "shifts": shifts,
        "network": selected_network,
        "sound_recorder": sound_recorder_name,
        "network_obj": network_obj,
        "shift_columns": shift_columns,
        "net_lookup": net_lookup,
        "shifts_by_network": shifts_by_network,
        "total_shifts": total_shifts,
        "is_weekly": True,  # جهت تشخیص گزارش هفتگی در فرانت‌اند (در صورت نیاز)
    })