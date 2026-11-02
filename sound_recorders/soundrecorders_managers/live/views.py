import logging
from decimal import Decimal
from datetime import datetime

import jdatetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from utils.db_connection import connect_db
from sound_recorders.live_program_audit.live_financial_calculation.forms import HeaderForm
from .forms import LiveDateFilterForm

logger = logging.getLogger(__name__)


def jalali_to_gregorian(value):
    if not value:
        return None
    try:
        if isinstance(value, (jdatetime.date, jdatetime.datetime)):
            return value.togregorian()
        year, month, day = map(int, str(value).replace("-", "/").split("/"))
        return jdatetime.date(year, month, day).togregorian()
    except (TypeError, ValueError):
        return None


def gregorian_to_jalali_str(value):
    if not value:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")


@login_required
def manager_live_summary(request):
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    form = LiveDateFilterForm(request.GET or None)
    programs = []
    error = None

    start_greg = jalali_to_gregorian(start_date)
    end_greg = jalali_to_gregorian(end_date)

    if start_date and not start_greg or end_date and not end_greg:
        error = "فرمت تاریخ واردشده معتبر نیست."
    elif start_greg and end_greg and start_greg > end_greg:
        error = "تاریخ شروع نباید بعد از تاریخ پایان باشد."
    else:
        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "EXEC dbo.Sp_Live_Programs_Monthly_Summary ?, ?, ?, ?",
                    (start_greg, end_greg, None, None),
                )
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    for row in cursor.fetchall():
                        program = dict(zip(columns, row))
                        pending_count = int(program.get("Pending_Payment_Count") or 0)
                        if pending_count <= 0:
                            continue
                        for field in ("Start_date", "End_date"):
                            if program.get(field):
                                program[field] = gregorian_to_jalali_str(program[field])
                        programs.append(program)
        except Exception:
            logger.exception("Manager live summary failed")
            error = "خطا در دریافت خلاصه برنامه‌های زنده."

    return render(
        request,
        "main/includes/sound_recorders/sound_recorder_manager/live/summary.html",
        {
            "title": "مدیریت برنامه‌های زنده",
            "form": form,
            "programs": programs,
            "start_date": start_date,
            "end_date": end_date,
            "error": error,
        },
    )


@login_required
def manager_live_details(request, id_manual_program):
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    start_greg = jalali_to_gregorian(start_date)
    end_greg = jalali_to_gregorian(end_date)
    context = {
        "header_form": HeaderForm(),
        "data": [],
        "row_count": 0,
        "total_amount_filtered": Decimal("0"),
        "total_amount_all": Decimal("0"),
        "selected_payment_status": "2",
        "start_date": start_date,
        "end_date": end_date,
        "manager_mode": True,
        "manager_summary_url": "sound_recorders:soundrecorders_manager:live:summary",
    }

    if (start_date and not start_greg) or (end_date and not end_greg):
        context["error"] = "فرمت تاریخ واردشده معتبر نیست."
        return render(
            request,
            "main/includes/sound_recorders/sound_recorder_manager/live/details.html",
            context,
        )
    if start_greg and end_greg and start_greg > end_greg:
        context["error"] = "تاریخ شروع نباید بعد از تاریخ پایان باشد."
        return render(
            request,
            "main/includes/sound_recorders/live_program_audit/live_program_details.html",
            context,
        )

    try:
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
                (int(id_manual_program), start_greg, end_greg, 2),
            )
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                rows = []

        for row in rows:
            if row.get("Live_shift_date"):
                row["Live_shift_date"] = gregorian_to_jalali_str(row["Live_shift_date"])

        total = sum(
            (Decimal(str(row.get("Final_Calculated_Rate") or 0)) for row in rows),
            Decimal("0"),
        )
        context.update({
            "data": rows,
            "row_count": len(rows),
            "total_amount_filtered": total,
            "total_amount_all": total,
        })
    except Exception:
            logger.exception("Manager live details failed")
            context["error"] = "خطا در دریافت جزئیات برنامه زنده."

    return render(
        request,
        "main/includes/sound_recorders/live_program_audit/live_program_details.html",
        context,
    )
