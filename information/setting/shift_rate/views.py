from django.db.models import Subquery, OuterRef
from django.contrib.auth.decorators import login_required
from .forms import ShiftRateFilterForm
from .models import ShiftRate, Shift_Types,CurrentJob,Levels
from information.employment_info.models import JobLevels

@login_required
def shift_rate_view(request):
    # دریافت پارامترهای فیلتر
    job_id = request.GET.get('job')
    level_id = request.GET.get('level')
    shift_type_id = request.GET.get('shift_type')
    # shift_name = request.GET.get('shift_name')
    shift_name = request.GET.get('shift_name')
    # ایجاد فرم با مقادیر انتخاب شده
    form = ShiftRateFilterForm(
        selected_job_id=job_id,
        selected_level_id=level_id,
        selected_shift_type_id=shift_type_id,
        selected_shift_name=shift_name
    )

    # گرفتن همه نرخ‌ها
    shift_rates = ShiftRate.objects.filter(active=True, del_field=False)

    # اعمال فیلترها
    if job_id:
        shift_rates = shift_rates.filter(id_current_job_id=job_id)
    if level_id:
        shift_rates = shift_rates.filter(id_levels_id=level_id)
    if shift_type_id:
        shift_rates = shift_rates.filter(id_shift_type=shift_type_id)
    if shift_name:
        shift_rates = shift_rates.filter(shift_name=shift_name)

    # تغییر بخش order_by در shift_rate_view
    shift_rates = shift_rates.annotate(
        sort_shift_id=Subquery(
            Shift.objects.filter(
                id_shift_type=OuterRef('id_shift_type'),
                shift_name=OuterRef('shift_name')
            ).values('id_shift')[:1]
        )
    ).order_by(
        'id_current_job__current_job',  # نام شغل
        'id_levels__levels',  # نام رده
        'id_shift_type',  # نوع شیفت
        'sort_shift_id'  # مرتب سازی بر اساس id_shift به دست آمده
    )
    # ایجاد مپ برای نوع شیفت
    shift_type_map = {}
    for st in Shift_Types.objects.filter(active=True, del_field=False):
        shift_type_map[st.id_shift_type] = st.shift_type_name
    # اینو اضافه کن - برای نمایش نام شیفت
    shift_name_map = {}
    for rate in shift_rates:
        shift_name_map[rate.shift_name] = rate.shift_name

    context = {
        'form': form,
        'shift_rates': shift_rates,
        'shift_type_map': shift_type_map,
        'shift_name_map': shift_name_map,
        'selected_params': {
            'job': job_id,
            'level': level_id,
            'shift_type': shift_type_id,
            'shift_name': shift_name,
        }
    }

    return render(request, 'main/includes/setting/shift_rate/shift_rate.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from information.employment_info.models import JobLevels, Levels
from sound_recorders.models import Shift


@require_GET
def get_levels(request):
    """دریافت رده‌های یک شغل"""
    job_id = request.GET.get('job_id')
    levels = []

    if job_id:
        # گرفتن رده‌های مربوط به این شغل
        job_levels = JobLevels.objects.filter(
            current_job_id=job_id,
            active=True,
            del_field=False
        ).select_related('level_id')

        for jl in job_levels:
            if jl.level_id and jl.level_id.active and not jl.level_id.del_field:
                levels.append({
                    'id': jl.level_id.id_levels,
                    'name': jl.level_id.levels
                })

    return JsonResponse({'levels': levels})


@require_GET
# def get_shift_names(request):
#     """دریافت شماره شیفت‌های یک نوع شیفت"""
#     shift_type_id = request.GET.get('shift_type_id')
#     shifts = []
#
#     if shift_type_id:
#         shift_data = list(Shift.objects.filter(
#             id_shift_type=shift_type_id,
#             active=True,
#             del_field=False
#         ).values_list('shift_number','shift_name').distinct().order_by('shift_number'))
#
#     return JsonResponse({'shifts': shifts})
def get_shift_names(request):
    """دریافت نام شیفت‌های یک نوع شیفت"""
    shift_type_id = request.GET.get('shift_type_id')
    names = []

    if shift_type_id:
        # گرفتن جفت (شماره, نام) و مرتب‌سازی بر اساس شماره
        shift_pairs = Shift.objects.filter(
            id_shift_type=shift_type_id,
            active=True,
            del_field=False
        ).values_list('shift_number', 'shift_name').distinct().order_by('shift_number')

        # اسم متغیر رو عوض کن تا با نام فیلد تداخل نکنه
        names = [shift_name for shift_number, shift_name in shift_pairs]  # اینجا shift_name

    return JsonResponse({'names': names})


from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import connection, transaction
from .models import ShiftRate



@login_required
@require_POST
def update_rate(request):
    """نسخه ساده با مقادیر ثابت برای Active و Del"""
    rate_id = request.POST.get('rate_id')
    shift_rate = request.POST.get('shift_rate')

    if not rate_id or not shift_rate:
        messages.error(request, 'اطلاعات ناقص است')
        return redirect_to_index(request)

    try:
        username = request.user.username

        # تمیز کردن
        cleaned_value = str(shift_rate).strip().replace(',', '').replace(' ', '')

        with connection.cursor() as cursor:
            # اطلاعات فعلی
            cursor.execute("""
                SELECT Id_shift_type, shift_name, Id_current_job, Id_levels
                FROM Tbl_Shift_Rate 
                WHERE Id_shift_rate = %s AND Active = 1 AND Del = 0
            """, [rate_id])

            row = cursor.fetchone()

            if not row:
                messages.error(request, 'رکورد مورد نظر یافت نشد')
                return redirect_to_index(request)

            # استور پروسیجر با پارامترهای کمتر
            # اگر Active و Del همیشه ۱ و ۰ هستند، مستقیماً بفرست
            cursor.execute("""
                EXEC Sp_UpdateShiftRate 
                    @Action = 'UPDATE',
                    @Id_shift_rate = %s,
                    @Id_shift_type = %s,
                    @shift_name = %s,
                    @Id_current_job = %s,
                    @Id_levels = %s,
                    @Shift_rate = %s,
                    @Active = 1,
                    @Del = 0,
                    @User_name = %s
            """, [
                rate_id,  # ۱
                row[0],  # ۲
                row[1],  # ۳
                row[2],  # ۴
                row[3],  # ۵
                cleaned_value,  # ۶
                username  # ۷ - فقط ۷ پارامتر چون Active و Del در query ثابت هستند
            ])
            # دقت: در بالا ۷ پارامتر داریم چون Active و Del در خود query نوشته شده‌اند

        messages.success(request, 'نرخ با موفقیت به‌روز شد')

    except Exception as e:
        messages.error(request, f'خطا: {str(e)}')

    return redirect_to_index(request)

@login_required
@require_POST
@transaction.atomic
def delete_rate(request):
    """حذف نرخ شیفت"""
    rate_id = request.POST.get('rate_id')

    if not rate_id:
        messages.error(request, 'شناسه رکورد مشخص نیست')
        return redirect_to_index(request)

    try:
        # ۱. پیدا کردن رکورد با ORM
        shift_rate = ShiftRate.objects.select_for_update().get(
            id_shift_rate=rate_id,
            active=True,
            del_field=False
        )

        # ۲. حذف با استور پروسیجر
        username = request.user.username

        with connection.cursor() as cursor:
            cursor.execute("""
                EXEC Sp_UpdateShiftRate 
                    @Action = 'DELETE',
                    @Id_shift_rate = %s,
                    @User_name = %s
            """, [
                shift_rate.id_shift_rate,
                username
            ])

        messages.success(request, 'رکورد با موفقیت حذف شد')

    except ShiftRate.DoesNotExist:
        messages.error(request, 'رکورد مورد نظر یافت نشد')
    except Exception as e:
        messages.error(request, f'خطا در حذف: {str(e)}')

    return redirect_to_index(request)


from django.shortcuts import redirect
from django.urls import reverse


def redirect_to_index(request):
    """هدایت به صفحه اصلی - نسخه ساده"""
    # همیشه مسیر مستقیم
    base_url = '/information/setting/shift_rate/'

    # جمع‌آوری پارامترهای فیلتر
    params = []
    for key in ['job', 'level', 'shift_type', 'shift_name']:
        value = request.GET.get(key)
        if value:
            params.append(f"{key}={value}")

    if params:
        base_url += '?' + '&'.join(params)

    return redirect(base_url)
@login_required
@require_POST
# def add_rate(request):
#     """استفاده از Django ORM"""
#     try:
#         job_id = int(request.POST['job_id'])
#         level_id = int(request.POST['level_id'])
#         shift_type_id = int(request.POST['shift_type_id'])
#         shift_name = int(request.POST['shift_name'])
#         shift_rate_str = request.POST['shift_rate']
#
#         # تمیز کردن نرخ
#         shift_rate_clean = str(shift_rate_str).replace(',', '').replace(' ', '')
#         shift_rate_value = int(float(shift_rate_clean))
#
#         # بررسی تکراری
#         exists = ShiftRate.objects.filter(
#             id_current_job_id=job_id,
#             id_levels_id=level_id,
#             id_shift_type=shift_type_id,
#             shift_name=shift_name,
#             active=True,
#             del_field=False
#         ).exists()
#
#         if exists:
#             messages.error(request, 'این ترکیب قبلاً ثبت شده است')
#             return redirect('/information/setting/shift_rate/')
#
#         # ایجاد رکورد جدید
#         ShiftRate.objects.create(
#             id_current_job_id=job_id,
#             id_levels_id=level_id,
#             id_shift_type=shift_type_id,
#             shift_name=shift_name,
#             shift_rate=shift_rate_value,
#             active=True,
#             del_field=False
#         )
#
#         messages.success(request, 'نرخ جدید با موفقیت اضافه شد')
#
#     except Exception as e:
#         messages.error(request, f'خطا: {str(e)}')
#
#     return redirect('/information/setting/shift_rate/')
def add_rate(request):
    """افزودن نرخ شیفت جدید با استور پروسیجر"""
    try:
        # دریافت داده‌ها
        job_id = request.POST.get('job_id')
        level_id = request.POST.get('level_id')
        shift_type_id = request.POST.get('shift_type_id')
        shift_name = request.POST.get('shift_name')
        shift_rate = request.POST.get('shift_rate')
        username = request.user.username

        # print(f"Parsed values: job_id={job_id}, level_id={level_id}, shift_type_id={shift_type_id}, shift_name={shift_name}, shift_rate={shift_rate}")

        # بررسی فیلدهای ضروری
        required_fields = [job_id, level_id, shift_type_id, shift_name, shift_rate]
        if not all(required_fields):
            messages.error(request, 'تمام فیلدها را پر کنید')
            return redirect_to_index(request)

        # تمیز کردن نرخ
        shift_rate_clean = str(shift_rate).replace(',', '').replace(' ', '')
        shift_rate_value = int(float(shift_rate_clean))  # ابتدا float سپس int

        # بررسی تکراری نبودن
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM Tbl_Shift_Rate
                WHERE Id_current_job = %s
                  AND Id_levels = %s
                  AND Id_shift_type = %s
                  AND shift_name = %s
                  AND Active = 1
                  AND Del = 0
            """, [job_id, level_id, shift_type_id, shift_name])

            count = cursor.fetchone()[0]
            print(f"Duplicate check count: {count}")
            if count > 0:
                messages.error(request, 'این ترکیب قبلاً ثبت شده است')
                return redirect('/information/setting/shift_rate/')

        # افزودن با استور پروسیجر
        with connection.cursor() as cursor:
            # اگر استور پروسیجر INSERT دارید
            cursor.execute("""
                EXEC Sp_UpdateShiftRate
                    @Action = 'INSERT',
                    @Id_shift_type = %s,
                    @shift_name = %s,
                    @Id_current_job = %s,
                    @Id_levels = %s,
                    @Shift_rate = %s,
                    @User_name = %s
            """, [
                shift_type_id,
                shift_name,
                job_id,
                level_id,
                shift_rate_value,
                username
            ])

            # یا اگر استور پروسیجر جداگانه INSERT دارید:
            # cursor.execute("EXEC Sp_InsertShiftRate %s, %s, %s, %s, %s, %s",
            #     [shift_type_id, shift_name, job_id, level_id, cleaned_rate, username])

        messages.success(request, 'نرخ جدید با موفقیت اضافه شد')

    except Exception as e:
        messages.error(request, f'خطا در افزودن: {str(e)}')

    return redirect('/information/setting/shift_rate/')

# from django.shortcuts import render, redirect
# from sound_recorders.models import *
# from utils.db_connection import connect_db
# from django.urls import reverse
# from django.http import HttpResponse
# import pandas as pd
# import json
# from django.core.paginator import Paginator
# from .forms import JobForm
# def shift_rate(request):
#     header_form = JobForm(request.POST or None)
#     if request.method == "POST" and header_form.is_valid():
#         action = request.POST.get("action")
#         current_job = header_form.cleaned_data.get("current_job")
#         levels = header_form.cleaned_data.get("levels")
#         shift_type = header_form.cleaned_data.get("shift_type")
#         shift_numbers = header_form.cleaned_data.get("shift_name")
#         shift_rate = header_form.cleaned_data.get("shift_rate")
#
#
#     return render(request, "main/includes/setting/shift_rate/shift_rate.html", {
#         "header_form": header_form,
#
#     })
# def job_form_view(request):
#     form = JobForm()
#
#     # اگر فرم ارسال شده
#     if request.method == 'POST':
#         form = JobForm(request.POST)
#
#         if form.is_valid():
#             # پردازش داده‌ها
#             current_job = form.cleaned_data['current_job']
#             job_level = form.cleaned_data['job_level']
#             shift_type = form.cleaned_data['shift_type']
#             shift_name = form.cleaned_data['shift_name']
#
#             # ذخیره یا پردازش
#             return render(request, 'success.html', {'form': form})
#
#     # GET request - ارسال داده‌های اضافی به تمپلیت
#     current_jobs = CurrentJob.objects.filter(active=True, del_field=False, is_seda=True)
#
#     # آماده‌سازی داده‌ها برای JavaScript
#     job_levels_map = {}
#     for job in current_jobs:
#         # دریافت رده‌های هر شغل
#         levels = Levels.objects.filter(
#             id_levels__in=Job_Levels.objects.filter(
#                 current_job=job,
#                 active=True,
#                 del_field=False
#             ).values_list('level_id', flat=True)
#         ).order_by('order')
#
#         job_levels_map[str(job.id_current_job)] = [
#             {'id': str(l.id_levels), 'name': l.levels}
#             for l in levels
#         ]
#
#     # داده‌های شیفت
#     shift_types = Shift_Type.objects.filter(active=True, del_field=False)
#     shifts_map = {}
#
#     for st in shift_types:
#         shifts = Shift.objects.filter(shift_type=st)
#         shifts_map[str(st.id_shift_type)] = [
#             {'id': str(s.id_shift), 'number': str(s.shift_name)}
#             for s in shifts
#         ]
#
#     return render(request, 'form.html', {
#         'form': form,
#         'job_levels_map': job_levels_map,
#         'shifts_map': shifts_map,
#     })
# setting/shift_rate/views.py
# views.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
#
# from .forms import ShiftRateFilterForm
# from .models import ShiftRate
# from sound_recorders.models import Shift_Type, Shift
# from information.employment_info.models import CurrentJob, JobLevels
#
#
# @login_required
# def shift_rate_view(request):
#     # دریافت فیلترها
#     job_id = request.GET.get('job')
#     level_id = request.GET.get('level')
#     shift_type_id = request.GET.get('shift_type')
#     shift_name = request.GET.get('shift_name')
#
#     # فرم فیلتر
#     form = ShiftRateFilterForm(initial={
#         'job': job_id,
#         'level': level_id,
#         'shift_type': shift_type_id,
#         'shift_name': shift_name
#     })
#
#     # گرفتن همه نرخ‌ها
#     shift_rates = ShiftRate.objects.filter(active=True, del_field=False)
#
#     # اعمال فیلترها
#     if job_id:
#         shift_rates = shift_rates.filter(id_current_job_id=job_id)
#     if level_id:
#         shift_rates = shift_rates.filter(id_levels_id=level_id)
#     if shift_type_id:
#         shift_rates = shift_rates.filter(id_shift_type=shift_type_id)
#     if shift_name:
#         shift_rates = shift_rates.filter(shift_name=shift_name)
#
#     # گرفتن نام نوع شیفت برای نمایش
#     shift_type_names = {}
#     for st in Shift_Type.objects.filter(active=True, del_field=False):
#         shift_type_names[st.id_shift_type] = st.shift_type_name
#
#     context = {
#         'form': form,
#         'shift_rates': shift_rates,
#         'shift_type_names': shift_type_names,
#     }
#     return render(request, 'main/includes/setting/shift_rate/shift_rate.html', context)
#
#
# @login_required
# def update_shift_rate(request):
#     if request.method == 'POST':
#         rate_id = request.POST.get('rate_id')
#         new_rate = request.POST.get('new_rate')
#
#         try:
#             shift_rate = ShiftRate.objects.get(id_shift_rate=rate_id)
#             shift_rate.shift_rate = new_rate
#             shift_rate.save()
#             return redirect('shift_rate')
#         except:
#             pass
#
#     return redirect('shift_rate')
#
#
# from django.http import JsonResponse
# from django.views.decorators.http import require_GET, require_POST
#
#
# @require_GET
# def get_levels(request):
#     job_id = request.GET.get('job_id')
#     levels = []
#
#     if job_id:
#         job_levels = JobLevels.objects.filter(
#             current_job_id=job_id,
#             active=True,
#             del_field=False
#         ).select_related('level_id')
#
#         for jl in job_levels:
#             levels.append({
#                 'id': jl.level_id.id_levels,
#                 'name': jl.level_id.levels
#             })
#
#     return JsonResponse({'levels': levels})
#
#
# @require_GET
# def get_shift_numbers(request):
#     shift_type_id = request.GET.get('shift_type_id')
#     numbers = []
#
#     if shift_type_id:
#         shifts = Shift.objects.filter(
#             id_shift_type=shift_type_id,
#             active=True,
#             del_field=False
#         ).values_list('shift_name', flat=True).distinct()
#
#         numbers = sorted(list(shifts))
#
#     return JsonResponse({'numbers': numbers})
#
#
# @require_POST
# def delete_shift_rate(request):
#     rate_id = request.POST.get('rate_id')
#
#     try:
#         rate = ShiftRate.objects.get(id_shift_rate=rate_id)
#         rate.active = False  # یا rate.del_field = True
#         rate.save()
#         return JsonResponse({'success': True})
#     except:
#         return JsonResponse({'success': False})