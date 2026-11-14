from decimal import Decimal
import jdatetime
from datetime import datetime, date, timedelta
from sound_recorders.live_program_audit.live_financial_calculation.forms import HeaderForm
from sound_recorders.live_program_audit.live_financial_calculation.models import LiveStatus, LivePaymentStatus
from sound_recorders.live_program_audit.main_live_programs.views import jalali_to_gregorian,to_number
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from utils.db_connection import connect_db
import logging
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

def get_previous_jalali_month_range():

    today = jdatetime.date.fromgregorian(
        date=timezone.localdate()
    )

    previous_month_last_day = today.replace(day=1) - timedelta(days=1)

    previous_month_first_day = previous_month_last_day.replace(day=1)

    return previous_month_first_day, previous_month_last_day

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



def live_programs_summary_view(request):
    default_start, default_end = get_previous_jalali_month_range()

    # در اولین ورود، بازه ماه شمسی قبل به‌صورت خودکار اعمال می‌شود.
    filter_data = request.GET.copy()
    if request.method == "POST":
        start_date = request.POST.get("start_date") or request.GET.get("start_date")
        end_date = request.POST.get("end_date") or request.GET.get("end_date")
    else:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

    start_date = start_date or default_start.strftime("%Y/%m/%d")
    end_date = end_date or default_end.strftime("%Y/%m/%d")

    filter_data["start_date"] = start_date
    filter_data["end_date"] = end_date

    id_live_status = (
        request.POST.get("live_status") or request.GET.get("live_status")
        or request.POST.get("id_live_status") or request.GET.get("id_live_status") or None
    )
    id_network = (
        request.POST.get("network") or request.GET.get("network")
        or request.POST.get("id_network") or request.GET.get("id_network") or None
    )

    if request.method == "POST" and request.POST.get("action") in ("confirm", "reject"):
        try:
            program_id = int(request.POST.get("id_manual_program"))
            target_status = 2 if request.POST["action"] == "confirm" else 1

            start_greg = jalali_to_gregorian(start_date)
            end_greg = jalali_to_gregorian(end_date)
            if not start_greg or not end_greg:
                raise ValueError("فرمت تاریخ معتبر نیست.")
            if start_greg > end_greg:
                raise ValueError("تاریخ شروع نباید بعد از تاریخ پایان باشد.")

            username = request.user.username if request.user.is_authenticated else "system"

            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    EXEC dbo.Sp_Update_Live_Payment_Status_By_Period
                        @Id_manual_program = ?,
                        @StartDate = ?,
                        @EndDate = ?,
                        @TargetStatus = ?,
                        @UserName = ?
                    """,
                    (program_id, start_greg, end_greg, target_status, username),
                )
                result = cursor.fetchone()
                changed = int(result[0]) if result and result[0] is not None else 0
                conn.commit()

            if changed:
                messages.success(request, f"وضعیت {changed} رکورد با موفقیت تغییر کرد.")
            else:
                messages.warning(
                    request,
                    "در بازه انتخاب‌شده رکوردی با وضعیت قابل تغییر پیدا نشد؛ سایر رکوردها بدون تغییر باقی ماندند."
                )
        except (TypeError, ValueError) as exc:
            messages.error(request, str(exc) or "اطلاعات ارسالی معتبر نیست.")
        except Exception:
            logger.exception("Live payment approval update failed")
            messages.error(request, "خطا در تغییر وضعیت پرداخت.")

        # بازگشت به همان فیلترها، حتی اگر درخواست POST از خود جدول ارسال شده باشد.
        for key in ("live_status", "network"):
            value = request.POST.get(key)
            if value:
                filter_data[key] = value
        return redirect(request.path + "?" + filter_data.urlencode())

    form = HeaderForm(filter_data)
    status_dict = {str(s.id_live_status): s.status for s in LiveStatus.objects.all()}
    start_greg = jalali_to_gregorian(start_date)
    end_greg = jalali_to_gregorian(end_date)

    programs = []
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC Sp_Live_Programs_Monthly_Summary %s, %s, %s, %s",
            [start_greg, end_greg, id_live_status, id_network]
        )
        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            prog = dict(zip(columns, row))
            prog["Has_Pending"] = int(prog.get("Pending_Payment_Count") or 0) > 0
            prog["Has_Estimate_Code"] = bool(str(prog.get("Prog_Code") or "").strip())
            status_id = prog.get("Id_live_status")
            prog["Status_Name"] = status_dict.get(str(status_id), "-") if status_id is not None else "-"
            prog["Start_date"] = (
                jdatetime.date.fromgregorian(date=prog["Start_date"]).strftime("%Y/%m/%d")
                if prog.get("Start_date") else "-"
            )
            prog["End_date"] = (
                jdatetime.date.fromgregorian(date=prog["End_date"]).strftime("%Y/%m/%d")
                if prog.get("End_date") else "-"
            )
            programs.append(prog)

    return render(request, "main/includes/sound_recorders/live_program_audit/live_programs_summary.html", {
        "programs": programs,
        "header_form": form,
        "filter_start_date": start_date,
        "filter_end_date": end_date,
        "filter_id_live_status": id_live_status,
        "filter_id_network": id_network,
    })


def live_program_details_view(request, id_manual_program):
    template_name = (
        "main/includes/sound_recorders/live_program_audit/"
        "live_program_details.html"
    )

    # دریافت فیلترها از URL
    header_form = HeaderForm(request.GET or None)

    # id_manual_program = request.GET.get("id_manual_program", "").strip()
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    selected_payment_status = request.GET.get(
        "live_payment_status", ""
    ).strip()

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
                    if row.get("Live_shift_date"):
                        row["Live_shift_date"] = gregorian_to_jalali_str(
                            row["Live_shift_date"]
                        )
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

