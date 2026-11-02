import jdatetime
from django.shortcuts import render, redirect
from .forms import HeaderForm
from utils.db_connection import connect_db


# خواندن دوره مالی فعال
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

        if row:
            return row[0], row[1]
    return None, None

def gregorian_to_jalali(date_obj):
    if not date_obj:
        return None

    return jdatetime.date.fromgregorian(date=date_obj)


def fetch_rows(start_date=None, end_date=None):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "EXEC Sp_Leaves_Read ?, ?",
            (start_date, end_date)
        )

        cols = [c[0] for c in cursor.description]

        return [
            dict(zip(cols, row))
            for row in cursor.fetchall()
        ]


def leaves(request):

    # -----------------------------
    # خواندن دوره مالی فعال
    # -----------------------------
    start_db, end_db = get_financial_period()

    # تاریخ جلالی برای فرم
    default_start = gregorian_to_jalali(start_db)
    default_end = gregorian_to_jalali(end_db)

    # تاریخ میلادی برای SP
    read_start = start_db.strftime("%Y-%m-%d") if start_db else None
    read_end = end_db.strftime("%Y-%m-%d") if end_db else None

    # -----------------------------
    # فرم هدر
    # -----------------------------
    if request.method == "POST":

        header_form = HeaderForm(request.POST)

        if header_form.is_valid():

            start_date_j = header_form.cleaned_data.get("start_date")
            end_date_j = header_form.cleaned_data.get("end_date")

            # اگر کاربر تاریخ تغییر داد
            if start_date_j:
                read_start = start_date_j.togregorian().strftime("%Y-%m-%d")

            if end_date_j:
                read_end = end_date_j.togregorian().strftime("%Y-%m-%d")

            action = request.POST.get("action")

            # -----------------------------
            # ذخیره اطلاعات
            # -----------------------------
            if action == "submit":

                with connect_db() as conn:

                    cursor = conn.cursor()

                    i = 0
                    inserted = 0

                    while True:

                        leaves_key = f"leaves_{i}"

                        # پایان ردیف‌ها
                        if leaves_key not in request.POST:
                            break

                        national_code = (
                            request.POST.get(f"national_code_{i}") or ""
                        ).strip()

                        employment_id = request.POST.get(
                            f"employment_id_{i}"
                        )

                        leaves_value = request.POST.get(leaves_key)

                        try:
                            employment_id = int(employment_id)

                            leaves_value = (
                                int(leaves_value)
                                if str(leaves_value).strip() != ""
                                else 0
                            )

                        except (TypeError, ValueError):
                            i += 1
                            continue

                        # ثبت در دیتابیس
                        if national_code:

                            cursor.execute(
                                """
                                EXEC Sp_Insert_Leaves ?, ?, ?, ?, ?
                                """,
                                (
                                    read_start,
                                    read_end,
                                    leaves_value,
                                    national_code,
                                    employment_id
                                )
                            )

                            inserted += 1

                        i += 1

                    conn.commit()
                return redirect(request.path)
    else:

        # فرم اولیه
        header_form = HeaderForm(
            default_start=default_start,
            default_end=default_end
        )

    # -----------------------------
    # خواندن جدول
    # -----------------------------
    leaves_rows = fetch_rows(read_start, read_end)

    # اگر خالی بود
    if not leaves_rows:
        leaves_rows = fetch_rows(None, None)

    # -----------------------------
    # ارسال به قالب
    # -----------------------------
    context = {
        "header_form": header_form,
        "leaves_rows": leaves_rows,
    }

    return render(
        request,
        "main/includes/sound_recorders/shift_audit/leaves/leaves.html",
        context
    )