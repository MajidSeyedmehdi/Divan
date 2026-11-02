from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SelectNetwork, ShiftNumber, NetworkShift
from django.shortcuts import render, redirect
import jdatetime
from datetime import date
import pyodbc
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db import connection,DatabaseError
from .forms import HeaderForm
import jdatetime as jd
from datetime import timedelta, datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from utils.db_connection import connect_db


@login_required

def gregorian_to_jalali(date_obj):
    if not date_obj:
        return None

    return jdatetime.date.fromgregorian(date=date_obj)

def manual_save(request):
    # =========================================================
    # 1. AJAX: گرفتن شیفت‌های مربوط به شبکه
    # =========================================================
    if (
            request.headers.get('x-requested-with') == 'XMLHttpRequest'
            or request.GET.get('action') == 'get_shifts'
    ):
        network_id = request.GET.get('network_id')
        shifts = []

        if network_id:
            try:
                shift_ids = NetworkShift.objects.filter(
                    id_network=int(network_id)
                ).values_list('id_shift', flat=True)

                shifts_qs = ShiftNumber.objects.filter(
                    id_shift__in=shift_ids
                )

                shifts = [
                    {'id': s.id_shift, 'name': str(s.shift_number)}
                    for s in shifts_qs
                ]
            except (ValueError, TypeError):
                pass

        return JsonResponse({'shifts': shifts})

    # =========================================================
    # 2. فرم اصلی و متغیرها
    # =========================================================
    default_start = jdatetime.date.today()

    header_form = HeaderForm(
        request.POST or request.GET or None,
        default_start=default_start
    )

    top_list = []
    bottom_list = []
    selected_id_raw = request.POST.get("selected_id", "").strip() if request.method == "POST" else request.GET.get("selected_id", "").strip()
    shift_recorder_name = "تعیین نشده"

    # =========================================================
    # 3. توابع دیتابیس
    # =========================================================

    def get_top_list(start_date, network, shift_number_obj):
        result = []
        start_date_gregorian = start_date.togregorian() if start_date else None
        network_id = network.id_network if network else None
        shift_num = int(shift_number_obj.shift_number) if shift_number_obj and hasattr(shift_number_obj, 'shift_number') else None

        if not start_date_gregorian or not network_id:
            return result

        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    EXEC dbo.Sp_Manual_Live_Show
                        @StartDate=?,
                        @Id_network=?,
                        @ShiftNumber=?
                    """,
                    start_date_gregorian,
                    network_id,
                    shift_num
                )
                columns = [column[0] for column in cursor.description]
                raw_programs = [dict(zip(columns, row)) for row in cursor.fetchall()]

                for row in raw_programs:
                    if row.get('Start_date'):
                        row['Start_date_jalali'] = jdatetime.date.fromgregorian(date=row['Start_date']).strftime('%Y/%m/%d')
                    else:
                        row['Start_date_jalali'] = '-'

                    if row.get('End_date'):
                        row['End_date_jalali'] = jdatetime.date.fromgregorian(date=row['End_date']).strftime('%Y/%m/%d')
                    else:
                        row['End_date_jalali'] = '-'

                    play_time = row.get('Play_time')
                    if play_time:
                        if hasattr(play_time, 'strftime'):
                            row['Play_time'] = play_time.strftime('%H:%M')
                        else:
                            time_str = str(play_time).split('.')[0]
                            row['Play_time'] = time_str.replace('AM', '').replace('PM', '').strip()[:5]

                    result.append(row)
        except Exception as e:
            print("--> Error in get_top_list:", e)

        return result

    def get_bottom_list(start_date, network, shift_number_obj, selected_id_str):
        result = []
        if not selected_id_str:
            return result

        start_date_gregorian = start_date.togregorian() if start_date else None
        network_id = network.id_network if network else None
        shift_num = int(shift_number_obj.shift_number) if shift_number_obj and hasattr(shift_number_obj, 'shift_number') else None

        selected_ids = [int(i.strip()) for i in selected_id_str.split(',') if i.strip().isdigit()]

        if not start_date_gregorian or not network_id or not selected_ids:
            return result

        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                for prog_id in selected_ids:
                    # فراخوانی استور Sp_Soundrecorder_assignment_Live برای دریافت اطلاعات سطر انتخابی
                    cursor.execute(
                        """
                        EXEC dbo.Sp_Soundrecorder_assignment_Live
                            @StartDate=?,
                            @Id_network=?,
                            @ShiftNumber=?,
                            @Id_manual_program=?
                        """,
                        start_date_gregorian,
                        network_id,
                        shift_num,
                        prog_id
                    )
                    columns = [column[0] for column in cursor.description]
                    raw_programs = [dict(zip(columns, row)) for row in cursor.fetchall()]

                    for row in raw_programs:
                        if row.get('Start_date'):
                            row['Start_date_jalali'] = jdatetime.date.fromgregorian(date=row['Start_date']).strftime('%Y/%m/%d')
                        else:
                            row['Start_date_jalali'] = '-'

                        if row.get('End_date'):
                            row['End_date_jalali'] = jdatetime.date.fromgregorian(date=row['End_date']).strftime('%Y/%m/%d')
                        else:
                            row['End_date_jalali'] = '-'

                        play_time = row.get('Play_time')
                        if play_time:
                            if hasattr(play_time, 'strftime'):
                                row['Play_time'] = play_time.strftime('%H:%M')
                            else:
                                time_str = str(play_time).split('.')[0]
                                row['Play_time'] = time_str.replace('AM', '').replace('PM', '').strip()[:5]

                        result.append(row)
        except Exception as e:
            print("--> Error in get_bottom_list:", e)

        return result

    # =========================================================
    # 4. پردازش فرم و اجرا
    # =========================================================
    assigned_program_id = None
    if header_form.is_valid():
        start_date = header_form.cleaned_data.get('start_date')
        network = header_form.cleaned_data.get('network')
        shift_number_obj = header_form.cleaned_data.get('shift_number')

        start_date_gregorian = start_date.togregorian() if start_date else None
        network_id = network.id_network if network else None

        if request.method == "POST":

            # دریافت اکشن از name="action" یا name="formAction"
            action = request.POST.get("action") or request.POST.get("formAction")

            if action == "assign_sound_recorder":

                id_manual_program = request.POST.get("confirm_program_id")
                id_sound_recorder = request.POST.get("confirm_recorder_id")

                if not id_sound_recorder or id_sound_recorder in ['None', 'null', '', '0']:
                    messages.error(  request, "صدابردار شیفت مشخص نشده است."  )

                elif id_manual_program and start_date_gregorian:
                    conn = None
                    cursor = None

                    try:
                        user_name = ( request.user.username if request.user.is_authenticated else "System"
                        )
                        # -----------------------------------------
                        # تبدیل روز هفته به فارسی
                        # -----------------------------------------
                        weekdays_fa = {
                            'Saturday': 'شنبه',
                            'Sunday': 'یکشنبه',
                            'Monday': 'دوشنبه',
                            'Tuesday': 'سه‌‌شنبه',
                            'Wednesday': 'چهارشنبه',
                            'Thursday': 'پنج‌شنبه',
                            'Friday': 'جمعه'
                        }

                        shift_day_en = start_date_gregorian.strftime('%A')
                        shift_day_fa = weekdays_fa.get(shift_day_en, "")
                        # -----------------------------------------
                        # اتصال به دیتابیس
                        # -----------------------------------------
                        conn = connect_db()
                        cursor = conn.cursor()
                        # -----------------------------------------
                        # استور اول
                        # ذخیره صدابردار
                        # -----------------------------------------
                        sql = """
                            EXEC dbo.Sp_Save_Soundrecorders_Live
                                @Id_manual_program = ?,
                                @Id_sound_recorder = ?,
                                @LiveShiftDate = ?,
                                @LiveShiftDay = ?,
                                @User_name = ?
                        """
                        params = (
                            int(id_manual_program),
                            int(id_sound_recorder),
                            str(start_date_gregorian),
                            shift_day_fa,
                            user_name
                        )
                        cursor.execute(sql, params)
                        # -----------------------------------------
                        # Commit
                        # -----------------------------------------
                        conn.commit()
                        assigned_program_id = str(id_manual_program)

                        current_ids = []

                        # IDهایی که قبل از این انتخاب در جدول پایین بودند
                        if selected_id_raw:
                            current_ids = [
                                x.strip()
                                for x in selected_id_raw.split(',')
                                if x.strip().isdigit()
                            ]

                        # اگر برنامه جدید قبلاً در لیست نیست، اضافه شود
                        if id_manual_program and str(id_manual_program) not in current_ids:
                            current_ids.append(str(id_manual_program))

                        # تبدیل دوباره به رشته comma-separated
                        selected_id_raw = ','.join(current_ids)

                        messages.success(
                            request,
                            "صدابردار شیفت با موفقیت ذخیره شد."
                        )
                    except Exception as e:
                        if conn:
                            try:
                                conn.rollback()
                            except Exception:
                                pass
                        messages.error(
                            request,
                            f"خطا در ذخیره‌سازی: {e}"
                        )
                    finally:
                        if cursor:
                            try:
                                cursor.close()
                            except Exception:
                                pass
                        if conn:
                            try:
                                conn.close()
                            except Exception:
                                pass

            elif action == "confirm_recorder_change":

                id_manual_program = request.POST.get( "confirm_program_id")
                id_sound_recorder = request.POST.get( "confirm_recorder_id")
                if not id_manual_program:
                    messages.error( request,"شناسه برنامه مشخص نشده است." )

                elif not id_sound_recorder:
                    messages.error( request, "صدابردار جدید مشخص نشده است."  )

                elif not start_date_gregorian:
                    messages.error(  request,"تاریخ مشخص نشده است."  )

                else:
                    try:
                        user_name = (
                            request.user.username
                            if request.user.is_authenticated
                            else "System"
                        )

                        with connect_db() as conn:
                            cursor = conn.cursor()
                            # =========================================
                            # تغییر صدابردار توسط Stored Procedure
                            # =========================================
                            cursor.execute(
                                """
                                EXEC dbo.Sp_Update_SoundRecorder_Live
                                    @Id_manual_program=?,
                                    @Id_sound_recorder=?,
                                    @Live_shift_date=?,
                                    @User_name=?
                                """,
                                (
                                    int(id_manual_program),
                                    int(id_sound_recorder),
                                    start_date_gregorian,
                                    user_name
                                )
                            )

                            # =========================================
                            # بررسی تعداد رکوردهای تغییر کرده
                            # =========================================
                            row = cursor.fetchone()
                            updated_rows = row[0] if row else 0
                            conn.commit()

                        if updated_rows > 0:
                            # =========================================
                            # برنامه فعلی را به لیست برنامه‌های پایین
                            # اضافه می‌کنیم و قبلی‌ها را نگه می‌داریم
                            # =========================================
                            current_ids = []
                            if selected_id_raw:
                                current_ids = [
                                    x.strip()
                                    for x in selected_id_raw.split(',')
                                    if x.strip().isdigit()
                                ]
                            if (
                                    id_manual_program
                                    and str(id_manual_program) not in current_ids
                            ):
                                current_ids.append(
                                    str(id_manual_program)
                                )
                            selected_id_raw = ','.join(current_ids)
                            messages.success(
                                request,
                                "صدابردار با موفقیت تغییر کرد."
                            )
                        else:
                            messages.warning(
                                request,
                                "رکوردی برای تغییر صدابردار پیدا نشد."
                            )
                    except Exception as e:
                        messages.error(
                            request,
                            f"خطا در تغییر صدابردار: {e}"
                        )

            elif action == "submit_bottom":
                prog_id = request.POST.get("selected_id")
                if prog_id:
                    selected_id_raw = prog_id

            elif action == "save":
                print("--- FULL POST DATA ---", request.POST)

                program_name = request.POST.get("program_name")
                target_network_id = request.POST.get("network_name") or network_id
                play_time = request.POST.get("play_time")
                time_duration = request.POST.get("time_duration")

                saturday = 1 if 'Saturday' in request.POST else 0
                sunday = 1 if 'Sunday' in request.POST else 0
                monday = 1 if 'Monday' in request.POST else 0
                tuesday = 1 if 'Tuesday' in request.POST else 0
                wednesday = 1 if 'Wednesday' in request.POST else 0
                thursday = 1 if 'Thursday' in request.POST else 0
                friday = 1 if 'Friday' in request.POST else 0

                if start_date_gregorian and target_network_id and program_name:
                    with connect_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            """
                            EXEC dbo.Sp_Insert_program_manual
                                @StartDate=?,
                                @Program_name=?,
                                @Id_network=?,
                                @Play_time=?,
                                @Time_duration=?,
                                @Saturday=?,
                                @Sunday=?,
                                @Monday=?,
                                @Tuesday=?,
                                @Wednesday=?,
                                @Thursday=?,
                                @Friday=?
                            """,
                            start_date_gregorian,
                            program_name,
                            int(target_network_id),
                            play_time,
                            int(time_duration) if time_duration else 0,
                            saturday, sunday, monday, tuesday, wednesday, thursday, friday
                        )
                        conn.commit()

            elif action == "extend":
                extend_start_date = date.today()
                program_name = request.POST.get("extend_program_name")
                target_network_id = request.POST.get("extend_network_name") or network_id
                play_time = request.POST.get("extend_play_time")
                time_duration = request.POST.get("extend_time_duration")

                saturday = 1 if request.POST.get("extend_Saturday") else 0
                sunday = 1 if request.POST.get("extend_Sunday") else 0
                monday = 1 if request.POST.get("extend_Monday") else 0
                tuesday = 1 if request.POST.get("extend_Tuesday") else 0
                wednesday = 1 if request.POST.get("extend_Wednesday") else 0
                thursday = 1 if request.POST.get("extend_Thursday") else 0
                friday = 1 if request.POST.get("extend_Friday") else 0

                if extend_start_date and target_network_id and program_name:
                    try:
                        with connect_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                """
                                EXEC dbo.Sp_Extend_program_manual
                                    @StartDate=?,
                                    @Program_name=?,
                                    @Id_network=?,
                                    @Play_time=?,
                                    @Time_duration=?,
                                    @Saturday=?,
                                    @Sunday=?,
                                    @Monday=?,
                                    @Tuesday=?,
                                    @Wednesday=?,
                                    @Thursday=?,
                                    @Friday=?
                                """,
                                extend_start_date,
                                program_name,
                                int(target_network_id),
                                play_time,
                                int(time_duration) if time_duration else 0,
                                saturday, sunday, monday, tuesday, wednesday, thursday, friday
                            )
                            conn.commit()
                    except Exception as e:
                        print("--> SQL Execution ERROR:", e)

        # دریافت داده‌های جدول بالا و پایین
        top_list = get_top_list(start_date, network, shift_number_obj)
        bottom_list = get_bottom_list(start_date, network, shift_number_obj, selected_id_raw)

        # مقداردهی نام صدابردار بالای صفحه از نتایج
        shift_recorder_name = "تعیین نشده"
        if top_list:
            for item in top_list:
                name = item.get('ShiftSoundRecorderName')
                if name and name != "تعیین نشده":
                    shift_recorder_name = name
                    break

    else:
        if request.method == "POST":
            print("--> Form validation errors:", header_form.errors)

    context = {
        "header_form": header_form,
        "networks": SelectNetwork.objects.all(),
        "top_list": top_list,
        "bottom_list": bottom_list,
        "selected_id": selected_id_raw,
        'shift_recorder_name': shift_recorder_name,
        'assigned_program_id': assigned_program_id,
    }

    return render(
        request,
        "main/includes/sound_recorders/live_program_audit/manual_live_programs.html",
        context
    )

def edit(request):
    default_start = jdatetime.date.today()

    header_form = HeaderForm(
        request.POST or request.GET or None,
        default_start=default_start
    )

    edit_list = []
    # --------------------------------------------------
    # 1. ذخیره ویرایش برنامه انتخاب‌شده
    # --------------------------------------------------
    if (request.method == "POST" and request.POST.get("action") == "save"):
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            # دریافت اطلاعات فرم
            id_manual_program = request.POST.get("id_manual_program", "" ).strip()
            program_name = request.POST.get("modalProgramNameInput", "" ).strip()
            end_date = request.POST.get("end_date", "").strip()
            play_time = request.POST.get("play_time", "").strip()
            time_duration = request.POST.get("time_duration", "").strip()
            if request.POST.get("type") == "1":
                program_type = "تک نرخ"
            else:
                program_type = None

            # اعتبارسنجی اولیه
            if not id_manual_program:
                raise ValueError(
                    "شناسه برنامه برای ویرایش ارسال نشده است."
                )
            if not program_name:
                raise ValueError("نام برنامه وارد نشده است.")

            id_manual_program = int(id_manual_program)
            time_duration = int(time_duration)

            # دریافت روزهای هفته
            saturday = request.POST.get("Saturday") == "1"
            sunday = request.POST.get("Sunday") == "1"
            monday = request.POST.get("Monday") == "1"
            tuesday = request.POST.get("Tuesday") == "1"
            wednesday = request.POST.get("Wednesday") == "1"
            thursday = request.POST.get("Thursday") == "1"
            friday = request.POST.get("Friday") == "1"

            # تبدیل تاریخ شمسی به میلادی در صورت نیاز
            # اگر end_date از DateField استاندارد Django می‌آید،
            # معمولاً مقدار آن میلادی است.
            #
            # اگر تاریخ به شکل شمسی مثل 1405/07/20 ارسال می‌شود،
            # باید قبل از اجرا آن را تبدیل کنیم.

            # دریافت روزهای هفته
            saturday = request.POST.get("Saturday") == "1"
            sunday = request.POST.get("Sunday") == "1"
            monday = request.POST.get("Monday") == "1"
            tuesday = request.POST.get("Tuesday") == "1"
            wednesday = request.POST.get("Wednesday") == "1"
            thursday = request.POST.get("Thursday") == "1"
            friday = request.POST.get("Friday") == "1"

            # اجرای استور ویرایش
            with connect_db() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    EXEC dbo.Sp_Edit_program_manual
                        @Id_manual_program = ?,
                        @EndDate = ?,
                        @Program_name = ?,
                        @Play_time = ?,
                        @Time_duration = ?,
                        @Type = ?,
                        @Saturday = ?,
                        @Sunday = ?,
                        @Monday = ?,
                        @Tuesday = ?,
                        @Wednesday = ?,
                        @Thursday = ?,
                        @Friday = ?
                    """,
                    (
                        id_manual_program,
                        end_date,
                        program_name,
                        play_time,
                        time_duration,
                        program_type,
                        saturday,
                        sunday,
                        monday,
                        tuesday,
                        wednesday,
                        thursday,
                        friday,
                    )
                )

                conn.commit()
            if is_ajax:
                return JsonResponse({"status": "success", "message": "اطلاعات برنامه با موفقیت ویرایش شد."})

            messages.success(
                request,
                "اطلاعات برنامه با موفقیت ویرایش شد."
            )

        except Exception as e:
            if is_ajax:
                return JsonResponse({"status": "error", "message": str(e)})
            messages.error(request, f"خطا در ویرایش برنامه: {e}")

    # --------------------------------------------------
    # 2. دریافت فهرست برنامه‌ها
    # --------------------------------------------------
    if request.method == "POST":
        if header_form.is_valid():
            network = header_form.cleaned_data.get("network")

            # دریافت نام برنامه
            program_name_filter = (
                request.POST.get("program_name", "").strip()
            )
            if not program_name_filter:
                program_name_filter = (
                        header_form.cleaned_data.get("program_name", "")
                        or ""
                ).strip()

            network_id = (
                network.id_network if network else None
            )

            # 👇 دریافت شیء وضعیت از cleaned_data فرم
            status_obj = header_form.cleaned_data.get("status")

            # استخراج شناسه وضعیت؛ اگر انتخاب نشده بود یا به صورت پیش‌فرض همان 1 در نظر گرفته شود
            live_status = status_obj.pk if status_obj else 1

            if network_id:
                try:
                    with connect_db() as conn:
                        cursor = conn.cursor()

                        # ارسال پارامترها به استور پروسیجر
                        cursor.execute(
                            """
                            EXEC dbo.Sp_Manual_Edit_Show
                                @Id_network = ?,
                                @ProgramName = ?,
                                @Id_live_status = ?
                            """,
                            (
                                network_id,
                                program_name_filter or None,
                                live_status,  # ارسال دقیق شناسه وضعیت (پیش‌فرض 1 یا مقدار انتخابی)
                            )
                        )

                        columns = [
                            column[0]
                            for column in cursor.description
                        ]

                        raw_programs = [
                            dict(zip(columns, row))
                            for row in cursor.fetchall()
                        ]

                        for row in raw_programs:
                            if row.get("Start_date"):
                                row["Start_date_jalali"] = (
                                    jdatetime.date.fromgregorian(
                                        date=row["Start_date"]
                                    ).strftime("%Y/%m/%d")
                                )
                            else:
                                row["Start_date_jalali"] = "-"

                            if row.get("End_date"):
                                row["End_date_jalali"] = (
                                    jdatetime.date.fromgregorian(
                                        date=row["End_date"]
                                    ).strftime("%Y/%m/%d")
                                )
                            else:
                                row["End_date_jalali"] = "-"

                            edit_list.append(row)

                except Exception as e:
                    print("--> Error in get_edit_list:", e)
                    messages.error(
                        request,
                        "خطا در دریافت فهرست برنامه‌ها."
                    )

    # --------------------------------------------------
    # 3. آماده‌سازی صفحه
    # --------------------------------------------------
    selected_id_raw = (
        request.POST.get("selected_id", "").strip()
        if request.method == "POST"
        else request.GET.get("selected_id", "").strip()
    )

    context = {
        "header_form": header_form,
        "networks": SelectNetwork.objects.all(),
        "selected_id": selected_id_raw,
        "edit_list": edit_list,
    }

    return render(
        request,
        "main/includes/sound_recorders/live_program_audit/edit.html",
        context
    )



