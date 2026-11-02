
import jdatetime
import pandas as pd

from django.contrib import messages
from django.db import transaction, connection
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ExcelUploadForm
from .models import TblProgramSpec


def jalali_to_gregorian(value):

    if pd.isna(value) or value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        value = value.replace('-', '/')

        year, month, day = map(
            int,
            value.split('/')
        )

        return jdatetime.date(
            year,
            month,
            day
        ).togregorian()

    except Exception:
        raise ValueError(
            f'تاریخ شمسی نامعتبر است: {value}'
        )


def to_number(value):

    if pd.isna(value) or value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(',', '')

    try:
        return int(float(value))
    except Exception:
        raise ValueError(
            f'مقدار عددی نامعتبر است: {value}'
        )

def import_program_spec_view(request):
    programs = []
    form = ExcelUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        action = request.POST.get("action")
        # -------------------------------------------------------------
        # حالت اول: کلیک روی دکمه "ورود اطلاعات" (آپلود اکسل)
        # -------------------------------------------------------------
        if action == "import_excel":
            if form.is_valid():
                excel_file = request.FILES.get("excel_file")
                selected_network = form.cleaned_data["network"]
                # selected_network_id = selected_network.pk
                selected_network_id = getattr(
                    selected_network, "id_network", selected_network.pk)
                try:
                    # خواندن اکسل
                    df = pd.read_excel(excel_file)
                    df.columns = df.columns.astype(str).str.strip()

                    required_columns = [
                        "نام برنامه",
                        "کدبرآورد",
                        "گروه",
                        "تاریخ شروع",
                        "تاریخ پایان",
                        "قسمت",
                        "مدت",
                        "عادی/ویژه",
                        "رده دستیار",
                        "رده1",
                        "رده 2",
                        "رده 3",
                        "رده 4",
                        "رده 5",
                        "ارشد",
                        "ساختار",
                        "نوع",
                    ]

                    missing_columns = [
                        col for col in required_columns if col not in df.columns
                    ]
                    if missing_columns:
                        raise ValueError(
                            "ستون‌های زیر در Excel پیدا نشدند: "
                            + "، ".join(missing_columns)
                        )

                    # تبدیل تاریخ‌ها
                    df["تاریخ شروع"] = df["تاریخ شروع"].apply(jalali_to_gregorian)
                    df["تاریخ پایان"] = df["تاریخ پایان"].apply(jalali_to_gregorian)

                    # آماده‌سازی پارامترها
                    data_list = []
                    user_name = (
                        request.user.username
                        if request.user.is_authenticated
                        else "system"
                    )

                    sp_sql = "EXEC dbo.Sp_ImportProgramSpec @Program_name=%s, @Code=%s, @Id_network=%s, @Group_network=%s, @Start_date=%s, @End_date=%s, @Permitted_count=%s, @Time_duration=%s, @Program_type=%s, @Price_level0=%s, @Price_level1=%s, @Price_level2=%s, @Price_level3=%s, @Price_level4=%s, @Price_level5=%s, @Price_level6=%s, @Structure=%s, @Type=%s, @User_name=%s"

                    inserted_count = 0

                    with connection.cursor() as cursor:
                        for index, row in df.iterrows():
                            params = [
                                str(row["نام برنامه"])
                                if pd.notna(row["نام برنامه"])
                                else None,
                                str(row["کدبرآورد"])
                                if pd.notna(row["کدبرآورد"])
                                else None,
                                selected_network_id,
                                str(row["گروه"]) if pd.notna(row["گروه"]) else None,
                                row["تاریخ شروع"],
                                row["تاریخ پایان"],
                                to_number(row["قسمت"]),
                                to_number(row["مدت"]),
                                str(row["عادی/ویژه"])
                                if pd.notna(row["عادی/ویژه"])
                                else None,
                                to_number(row["رده دستیار"]),
                                to_number(row["رده1"]),
                                to_number(row["رده 2"]),
                                to_number(row["رده 3"]),
                                to_number(row["رده 4"]),
                                to_number(row["رده 5"]),
                                to_number(row["ارشد"]),
                                str(row["ساختار"])
                                if pd.notna(row["ساختار"])
                                else None,
                                str(row["نوع"]) if pd.notna(row["نوع"]) else None,
                                user_name,
                            ]
                            cursor.execute(sp_sql, params)
                            inserted_count += 1

                    messages.success(
                        request, f"{inserted_count} رکورد با موفقیت ثبت شد."
                    )

                    # ریدایرکت مستقیم با اسم url
                    # return redirect("soundrecorders:main_program_audit:import_excel")
                    return redirect(request.path)
                except Exception as e:
                    messages.error(request, f"خطا در ورود اطلاعات: {e}")

            else:
                messages.error(request, "لطفاً فایل اکسل و شبکه را به درستی انتخاب کنید.")
            # -------------------------------------------------------------
            # حالت دوم: کلیک روی دکمه "جستجو"
            # -------------------------------------------------------------
        elif action == "search":
            selected_network_id = request.POST.get("network")

            if selected_network_id:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("EXEC dbo.Sp_Search_Program_Spec @id_network=%s", [selected_network_id])

                        # مپ کردن خروجی Cursor به Dictionary جهت استفاده راحت در Template
                        columns = [col[0].lower() for col in cursor.description]
                        results = cursor.fetchall()

                        programs = []
                        for row in results:
                            item = dict(zip(columns, row))
                            # تبدیل تاریخ میلادی به شمسی برای نمایش در جدول
                            if item.get('start_date'):
                                item['start_date_jalali'] = jdatetime.date.fromgregorian(
                                    date=item['start_date']).strftime('%Y/%m/%d')
                            if item.get('end_date'):
                                item['end_date_jalali'] = jdatetime.date.fromgregorian(date=item['end_date']).strftime(
                                    '%Y/%m/%d')

                            programs.append(item)

                except Exception as e:
                    messages.error(request, f"خطا در دریافت اطلاعات جستجو: {e}")
            else:
                messages.error(request, "لطفاً یک شبکه را برای جستجو انتخاب کنید.")

    # اگر متد GET بود یا هنوز جستجویی انجام نشده بود (پیش‌فرض ۵۰ مورد آخر از ORM)
    if not programs and request.method != "POST":
        programs = TblProgramSpec.objects.all()[:100]

    return render(
        request,
        "main/includes/sound_recorders/live_program_audit/main_program_audit.html",
        {"form": form, "programs": programs},
    )
