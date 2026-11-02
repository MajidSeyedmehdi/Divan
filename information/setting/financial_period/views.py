from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .forms import FinancialPeriodForm
from information.setting.models import FinancialPeriod
import jdatetime


def get_last_month_range():
    """
    محاسبه اولین و آخرین روز ماه قبل
    """
    today = jdatetime.date.today()

    # محاسبه اولین روز ماه جاری
    first_day_of_current_month = jdatetime.date(today.year, today.month, 1)

    # آخرین روز ماه قبل = اولین روز ماه جاری منهای یک روز
    last_day_of_last_month = first_day_of_current_month - jdatetime.timedelta(days=1)

    # اولین روز ماه قبل
    first_day_of_last_month = jdatetime.date(
        last_day_of_last_month.year,
        last_day_of_last_month.month,
        1
    )

    return first_day_of_last_month, last_day_of_last_month


def create_financial_period(request):
    if request.method == 'POST':
        form = FinancialPeriodForm(request.POST)
        if form.is_valid():
            try:
                # گرفتن مقادیر مستقیماً از cleaned_data
                raw_start = form.cleaned_data['start_date']
                raw_end = form.cleaned_data['end_date']

                # اطمینان از تبدیل صحیح تاریخ شمسی انتخابی کاربر به میلادی
                if isinstance(raw_start, jdatetime.date):
                    start_date = raw_start.togregorian()
                else:
                    start_date = raw_start

                if isinstance(raw_end, jdatetime.date):
                    end_date = raw_end.togregorian()
                else:
                    end_date = raw_end

                description = form.cleaned_data.get('description', '')

                # اجرا با استفاده از پارامترهای ایمن SQL (جلوگیری از SQL Injection و فرمت اشتباه تاریخ)
                with connection.cursor() as cursor:
                    cursor.execute(
                        "EXEC Sp_Insert_FinancialPeriod @start_date=%s, @end_date=%s, @description=%s, @user_name=%s",
                        [start_date, end_date, description, request.user.username]
                    )

                messages.success(request, 'دوره مالی با موفقیت ایجاد شد.')
                return redirect('information:setting:financial_Period:create_financial_period')

            except Exception as e:
                messages.error(request, f"خطا در ایجاد دوره مالی: {str(e)}")
    else:
        # حالت GET: محاسبه و مقداردهی اولیه فقط برای نمایش در فرم
        start_date, end_date = get_last_month_range()

        form = FinancialPeriodForm(initial={
            'start_date': start_date,
            'end_date': end_date,
            'description': f"دوره مالی ({start_date.year}/{start_date.month:02d})"
        })

    return render(request, 'main/includes/setting/financial_period/financial_period.html', {'form': form})