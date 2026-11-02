from decimal import Decimal
import jdatetime
from datetime import datetime, date, timedelta
from sound_recorders.live_program_audit.live_financial_calculation.forms import HeaderForm
from sound_recorders.live_program_audit.live_financial_calculation.models import LiveStatus, LivePaymentStatus
from sound_recorders.live_program_audit.main_live_programs.views import jalali_to_gregorian,to_number
from django.shortcuts import render
from django.db import connection
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
    # دریافت فیلترها از query string
    start_date = request.GET.get('start_date', None) or None
    end_date = request.GET.get('end_date', None) or None
    id_live_status = request.GET.get('id_live_status', None) or None
    id_network = request.GET.get('id_network', None) or None
    form = HeaderForm(request.GET or None)
    # دیکشنری وضعیت‌ها برای تبدیل ID به متن
    status_dict = {str(s.id_live_status): s.status for s in LiveStatus.objects.all()}
    programs = []
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC Sp_Live_Programs_Monthly_Summary %s, %s, %s, %s",
            [start_date, end_date, id_live_status, id_network]
        )
        columns = [col[0] for col in cursor.description]
        # programs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        for row in cursor.fetchall():
            prog = dict(zip(columns, row))

            # ۱. تبدیل وضعیت (فقط یک خط)
            # ۱. تبدیل وضعیت (تبدیل ID به رشته برای تطبیق با دیکشنری)
            status_id = prog.get('Id_live_status')
            prog['Status_Name'] = status_dict.get(str(status_id), '-') if status_id is not None else '-'

            # ۲. تبدیل تاریخ‌ها به شمسی (فقط یک خط برای هر کدام)
            prog['Start_date'] = jdatetime.date.fromgregorian(date=prog['Start_date']).strftime('%Y/%m/%d') if prog.get(
                'Start_date') else '-'
            prog['End_date'] = jdatetime.date.fromgregorian(date=prog['End_date']).strftime('%Y/%m/%d') if prog.get(
                'End_date') else '-'

            programs.append(prog)
    context = {
        'programs': programs,
        'header_form' : form,
        'filter_start_date': start_date,
        'filter_end_date': end_date,
        'filter_id_live_status': id_live_status,
        'filter_id_network': id_network,
    }
    return render(request, 'main/includes/sound_recorders/live_program_audit/live_programs_summary.html', context)


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
        # فیلتر وضعیت پرداخت
        # if selected_payment_status:
        #     status_obj = LivePaymentStatus.objects.filter(
        #         pk=selected_payment_status
        #     ).first()
        #
        #     if status_obj is None:
        #         context["error"] = "وضعیت پرداخت انتخاب‌شده معتبر نیست."
        #         context["data"] = []
        #         context["row_count"] = 0
        #         context["total_amount_filtered"] = Decimal("0")
        #         return render(request, template_name, context)
        #
        #     selected_status_text = str(
        #         status_obj.payment_status or ""
        #     ).strip()
        #
        #     selected_status_id = str(
        #         status_obj.pk
        #     ).strip()
        #
        #     data = []
        #
        #     for row in rows:
        #         payment_status_value = str(
        #             row.get("Live_Payment_Status") or ""
        #         ).strip()
        #
        #         # پشتیبانی از خروجی‌ای که متن وضعیت یا شناسه وضعیت دارد
        #         if (
        #             payment_status_value == selected_status_text
        #             or payment_status_value == selected_status_id
        #         ):
        #             data.append(row)
        # else:
        #     data = rows

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

