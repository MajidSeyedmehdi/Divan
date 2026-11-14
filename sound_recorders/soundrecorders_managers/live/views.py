# import logging
# from decimal import Decimal
# from datetime import datetime
#
# import jdatetime
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
#
# from utils.db_connection import connect_db
# from sound_recorders.live_program_audit.live_financial_calculation.forms import HeaderForm
# from .forms import LiveDateFilterForm
#
# logger = logging.getLogger(__name__)
#
#
# def jalali_to_gregorian(value):
#     if not value:
#         return None
#     try:
#         if isinstance(value, (jdatetime.date, jdatetime.datetime)):
#             return value.togregorian()
#         year, month, day = map(int, str(value).replace("-", "/").split("/"))
#         return jdatetime.date(year, month, day).togregorian()
#     except (TypeError, ValueError):
#         return None
#
#
# def gregorian_to_jalali_str(value):
#     if not value:
#         return ""
#     if isinstance(value, datetime):
#         value = value.date()
#     return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")
#
#
# @login_required
# def manager_live_summary(request):
#     start_date = request.GET.get("start_date", "").strip()
#     end_date = request.GET.get("end_date", "").strip()
#     form = LiveDateFilterForm(request.GET or None)
#     programs = []
#     error = None
#
#     start_greg = jalali_to_gregorian(start_date)
#     end_greg = jalali_to_gregorian(end_date)
#
#     if start_date and not start_greg or end_date and not end_greg:
#         error = "فرمت تاریخ واردشده معتبر نیست."
#     elif start_greg and end_greg and start_greg > end_greg:
#         error = "تاریخ شروع نباید بعد از تاریخ پایان باشد."
#     else:
#         try:
#             with connect_db() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "EXEC dbo.Sp_Live_Programs_Monthly_Summary ?, ?, ?, ?",
#                     (start_greg, end_greg, None, None),
#                 )
#                 if cursor.description:
#                     columns = [column[0] for column in cursor.description]
#                     for row in cursor.fetchall():
#                         program = dict(zip(columns, row))
#                         pending_count = int(program.get("Pending_Payment_Count") or 0)
#                         if pending_count <= 0:
#                             continue
#                         for field in ("Start_date", "End_date"):
#                             if program.get(field):
#                                 program[field] = gregorian_to_jalali_str(program[field])
#                         programs.append(program)
#         except Exception:
#             logger.exception("Manager live summary failed")
#             error = "خطا در دریافت خلاصه برنامه‌های زنده."
#
#     return render(
#         request,
#         "main/includes/sound_recorders/sound_recorder_manager/live/summary.html",
#         {
#             "title": "مدیریت برنامه‌های زنده",
#             "form": form,
#             "programs": programs,
#             "start_date": start_date,
#             "end_date": end_date,
#             "error": error,
#         },
#     )
#
#
# @login_required
# def manager_live_details(request, id_manual_program):
#     start_date = request.GET.get("start_date", "").strip()
#     end_date = request.GET.get("end_date", "").strip()
#     start_greg = jalali_to_gregorian(start_date)
#     end_greg = jalali_to_gregorian(end_date)
#     context = {
#         "header_form": HeaderForm(),
#         "data": [],
#         "row_count": 0,
#         "total_amount_filtered": Decimal("0"),
#         "total_amount_all": Decimal("0"),
#         "selected_payment_status": "2",
#         "start_date": start_date,
#         "end_date": end_date,
#         "manager_mode": True,
#         "manager_summary_url": "sound_recorders:soundrecorders_manager:live:summary",
#     }
#
#     if (start_date and not start_greg) or (end_date and not end_greg):
#         context["error"] = "فرمت تاریخ واردشده معتبر نیست."
#         return render(
#             request,
#             "main/includes/sound_recorders/sound_recorder_manager/live/details.html",
#             context,
#         )
#     if start_greg and end_greg and start_greg > end_greg:
#         context["error"] = "تاریخ شروع نباید بعد از تاریخ پایان باشد."
#         return render(
#             request,
#             "main/includes/sound_recorders/sound_recorder_manager/live/details.html",
#             context,
#         )
#
#     try:
#         with connect_db() as conn:
#             cursor = conn.cursor()
#             cursor.execute(
#                 """
#                 EXEC dbo.Sp_Live_Program_Sound_Recorders_Detail
#                     @Id_manual_program = ?,
#                     @StartDate = ?,
#                     @EndDate = ?,
#                     @Id_live_payment_status = ?
#                 """,
#                 (int(id_manual_program), start_greg, end_greg, 2),
#             )
#             if cursor.description:
#                 columns = [column[0] for column in cursor.description]
#                 rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
#             else:
#                 rows = []
#
#         for row in rows:
#             if row.get("Live_shift_date"):
#                 row["Live_shift_date"] = gregorian_to_jalali_str(row["Live_shift_date"])
#
#         total = sum(
#             (Decimal(str(row.get("Final_Calculated_Rate") or 0)) for row in rows),
#             Decimal("0"),
#         )
#         context.update({
#             "data": rows,
#             "row_count": len(rows),
#             "total_amount_filtered": total,
#             "total_amount_all": total,
#         })
#     except Exception:
#             logger.exception("Manager live details failed")
#             context["error"] = "خطا در دریافت جزئیات برنامه زنده."
#
#     return render(
#         request,
#         "main/includes/sound_recorders/sound_recorder_manager/live/details.html",
#         context,
#     )
import jdatetime
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, date, timedelta
from sound_recorders.live_program_audit.manual_live_programs.models import SelectNetwork
from sound_recorders.live_program_audit.live_financial_calculation.models import LivePaymentStatus
from .forms import HeaderForm
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

def gregorian_to_jalali_str(date_value, fmt="%Y/%m/%d"):
    if not date_value:
        return ""

    try:
        if isinstance(date_value, datetime):
            date_value = date_value.date()

        return jdatetime.date.fromgregorian(
            date=date_value
        ).strftime(fmt)

    except Exception:
        logger.exception(
            "Error converting to Jalali: %s", date_value
        )
        return ""


def get_user_manager_id(cursor, user):
    """
    پیدا کردن Id_manager کاربر بر اساس گروه کاربر در جنگو
    """

    if not user.is_authenticated:
        return None

    group = user.groups.first()

    if not group:
        return None

    group_name = group.name

    cursor.execute("""
        SELECT TOP 1 Id_manager
        FROM dbo.Tbl_Manager
        WHERE Active = 1
          AND Del = 0
          AND ? LIKE '%' + Manager + '%'
        ORDER BY Id_manager
    """, (group_name,))

    row = cursor.fetchone()

    return row[0] if row else None


def soundrecorders_managers_live(request):
    default_start = jdatetime.date.today()

    # بازیابی آخرین جستجوی ذخیره‌شده
    saved_search = request.session.get("live_audit_search")

    if request.method == "POST":
        form_data = request.POST

    elif request.method == "GET" and saved_search:
        form_data = saved_search

    else:
        form_data = None

    header_form = HeaderForm(
        form_data,
        default_start=default_start
    )

    data_rows = []

    network = None
    network_id = None
    logged_in_manager_id = None

    show_last_column = True

    def to_gregorian(value):

        if value is None:
            return None

        if hasattr(value, "togregorian"):
            return value.togregorian()

        return value

    def load_programs(cursor, cleaned_data):

        nonlocal network
        nonlocal network_id
        nonlocal data_rows

        network = cleaned_data.get("network")
        network_id = network.pk if network else None

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        start_gregorian = to_gregorian(start_date)
        end_gregorian = to_gregorian(end_date)

        status_obj = cleaned_data.get("status")
        live_status = status_obj.pk if status_obj else 2

        if start_gregorian is None or end_gregorian is None:
            raise ValueError(
                "تاریخ شروع و پایان باید مشخص باشند."
            )

        if start_gregorian > end_gregorian:
            raise ValueError(
                "تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد."
            )

        cursor.execute(
            """
            EXEC dbo.Sp_Soundrecorders_Manager_Live
                @start_date = ?,
                @Id_manager = ?,
                @Id_network = ?,
                @end_date = ?,
                @Id_live_status = ?,
                @Id_live_payment_status = ?
            """,
            (
                start_gregorian,
                logged_in_manager_id,
                network_id,
                end_gregorian,
                live_status,
                2
            )
        )

        if cursor.description is None:
            raise ValueError(
                "استور نمایش برنامه‌ها خروجی جدولی برنگرداند."
            )

        columns = [
            column[0] for column in cursor.description
        ]

        data_rows = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        for row in data_rows:

            row["Start_date_jalali"] = gregorian_to_jalali_str(
                row.get("Start_date")
            )

            row["End_date_jalali"] = gregorian_to_jalali_str(
                row.get("End_date")
            )

    try:

        with connect_db() as conn:

            cursor = conn.cursor()

            logged_in_manager_id = get_user_manager_id(
                cursor,
                request.user
            )

            if logged_in_manager_id is None:

                messages.error(
                    request,
                    "برای کاربر جاری مدیر تعریف نشده است."
                )

            elif request.method == "POST":

                action = request.POST.get("action")

                id_sound_shift_live = request.POST.get(
                    "id_sound_shift_live"
                )

                if not header_form.is_valid():

                    messages.warning(
                        request,
                        "اطلاعات فرم معتبر نیست. تاریخ‌ها و فیلترها را بررسی کنید."
                    )

                else:

                    cleaned_data = header_form.cleaned_data

                    start_date = cleaned_data.get("start_date")
                    end_date = cleaned_data.get("end_date")

                    start_gregorian = to_gregorian(start_date)
                    end_gregorian = to_gregorian(end_date)

                    # ---------------------------------
                    # اعتبارسنجی بازه زمانی
                    # ---------------------------------

                    if (
                        start_gregorian is None
                        or end_gregorian is None
                    ):

                        messages.error(
                            request,
                            "تاریخ شروع و پایان به درستی ارسال نشده‌اند."
                        )

                    elif start_gregorian > end_gregorian:

                        messages.error(
                            request,
                            "تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد."
                        )

                    # ---------------------------------
                    # 1. جستجو
                    # ---------------------------------

                    elif action == "search":

                        request.session["live_audit_search"] = {
                            key: request.POST.get(key, "")
                            for key in header_form.fields.keys()
                        }

                        request.session.modified = True

                        load_programs(
                            cursor,
                            cleaned_data
                        )

                    # ---------------------------------
                    # 3. تأیید برنامه
                    # ---------------------------------

                    elif action == "confirm":

                        if not id_sound_shift_live:

                            messages.error(
                                request,
                                "شناسه برنامه انتخاب‌شده معتبر نیست."
                            )

                        else:

                            try:

                                cursor.execute(
                                    """
                                    EXEC dbo.Sp_Live_Confirm
                                        @Id_sound_shift_live = ?,
                                        @Id_manager = ?,
                                        @start_date = ?,
                                        @end_date = ?
                                    """,
                                    (
                                        int(id_sound_shift_live),
                                        int(logged_in_manager_id),
                                        start_gregorian,
                                        end_gregorian
                                    )
                                )

                                conn.commit()

                                messages.success(
                                    request,
                                    "برنامه با موفقیت تأیید شد و تمام قسمت‌های آن در بازه انتخابی به مدیر بعدی منتقل شدند."
                                )

                            except Exception:

                                conn.rollback()

                                raise

                    # ---------------------------------
                    # 4. رد برنامه
                    # ---------------------------------

                    elif action == "reject":

                        messages.warning(
                            request,
                            "عملیات رد برنامه هنوز پیاده‌سازی نشده است."
                        )

                    else:

                        messages.warning(
                            request,
                            "عملیات درخواستی معتبر نیست."
                        )

                    # ---------------------------------
                    # 5. بارگذاری مجدد جدول
                    # ---------------------------------

                    if action in ("open", "confirm", "reject"):

                        load_programs(
                            cursor,
                            cleaned_data
                        )

            # ---------------------------------
            # بازیابی نتایج جستجوی قبلی هنگام بازگشت
            # ---------------------------------
            elif request.method == "GET" and saved_search:

                if header_form.is_valid():

                    load_programs(
                        cursor,
                        header_form.cleaned_data
                    )

    except Exception as exc:

        logger.exception(
            "خطا در ویوی مدیریت برنامه‌های زنده"
        )

        messages.error(
            request,
            f"هنگام انجام عملیات خطایی رخ داد: {str(exc)}"
        )

    context = {
        "header_form": header_form,
        "network": network,
        "network_id": network_id,
        "data_rows": data_rows,
        "logged_in_manager_id": logged_in_manager_id,
        "show_last_column": show_last_column,
    }

    return render(
        request,
        "main/includes/sound_recorders/sound_recorder_manager/live/soundmanager_live.html",
        context
    )


def live_details(request):
    template_name = (
        "main/includes/sound_recorders/sound_recorder_manager/live/details.html"
    )

    selected_payment_status = request.GET.get("payment_status")

    if selected_payment_status is None:
        selected_payment_status = "2"

    header_form = HeaderForm(
        {
            **request.GET.dict(),
            "payment_status": selected_payment_status
        }
    )

    id_manual_program = request.GET.get("id_manual_program", "").strip()
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    Total_Rows =request.GET.get("Total_Rows", "").strip()


    # مقادیر پیش‌فرض برای قالب
    context = {
        "header_form": header_form,
        "data": [],
        "row_count": 0,
        "total_amount_filtered": Decimal("0"),
        "total_amount_all": Decimal("0"),
        "selected_payment_status": selected_payment_status,
        "start_date": start_date,
        "end_date": end_date,
        "Total_Rows": Total_Rows,
    }

    try:
        # شناسه برنامه الزامی است
        if not id_manual_program:
            context["error"] = "شناسه برنامه دریافت نشده است."
            return render(request, template_name, context)

        try:
            id_manual_program = int(id_manual_program)
        except (TypeError, ValueError):
            context["error"] = "شناسه برنامه معتبر نیست."
            return render(request, template_name, context)

        # تبدیل تاریخ شمسی به میلادی
        start_date_greg = (
            jalali_to_gregorian(start_date) if start_date else None
        )
        end_date_greg = (
            jalali_to_gregorian(end_date) if end_date else None
        )

        # بررسی بازه تاریخ
        if (
            start_date_greg
            and end_date_greg
            and start_date_greg > end_date_greg
        ):
            context["error"] = "تاریخ شروع نباید بعد از تاریخ پایان باشد."
            return render(request, template_name, context)

        # اجرای Stored Procedure
        with connect_db() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                EXEC dbo.Sp_Live_Program_Sound_Recorders_Detail
                    @Id_manual_program = ?,
                    @StartDate = ?,
                    @EndDate = ?,
                    @Id_live_payment_status = ?
                """,
                (
                    id_manual_program,
                    start_date_greg,
                    end_date_greg,
                    int(selected_payment_status) if selected_payment_status else None,
                ),
            )

            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

                for row in rows:
                    live_date = row.get("Live_shift_date")

                    if live_date:
                        row["Live_shift_date"] = jdatetime.date.fromgregorian(
                            date=live_date
                        ).strftime("%Y/%m/%d")
            else:
                rows = []

            cursor.close()

        # محاسبه مبلغ کل قبل از فیلتر وضعیت پرداخت
        def amount_of(row):
            value = row.get("Final_Calculated_Rate")
            return Decimal(str(value or 0))

        context["total_amount_all"] = sum(
            (amount_of(row) for row in rows),
            Decimal("0"),
        )

        # فیلتر وضعیت پرداخت
        if selected_payment_status:
            status_obj = LivePaymentStatus.objects.filter(
                pk=selected_payment_status
            ).first()

            if status_obj is None:
                context["error"] = "وضعیت پرداخت انتخاب‌شده معتبر نیست."
                context["data"] = []
                context["row_count"] = 0
                context["total_amount_filtered"] = Decimal("0")
                return render(request, template_name, context)

            selected_status_text = str(
                status_obj.live_payment_status or ""
            ).strip()

            selected_status_id = str(
                status_obj.pk
            ).strip()

            data = []

            for row in rows:
                payment_status_value = str(
                    row.get("Payment_Status") or ""
                ).strip()

                # پشتیبانی از خروجی‌ای که متن وضعیت یا شناسه وضعیت دارد
                if (
                    payment_status_value == selected_status_text
                    or payment_status_value == selected_status_id
                ):
                    data.append(row)
        else:
            data = rows

        # آمار رکوردهای پس از فیلتر
        context["data"] = data
        context["row_count"] = len(data)
        context["total_amount_filtered"] = sum(
            (amount_of(row) for row in data),
            Decimal("0"),
        )

        return render(request, template_name, context)

    except Exception as e:
        logger.exception("Error in live_details")
        context["error"] = f"خطا در پردازش درخواست: {str(e)}"
        return render(request, template_name, context)


