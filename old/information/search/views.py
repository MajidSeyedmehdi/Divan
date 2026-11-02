#
# conn_str = (
#                 f"DRIVER={db_settings['OPTIONS']['driver']};"
#                 f"SERVER={db_settings['HOST']},{db_settings['PORT']};"
#                 f"DATABASE={db_settings['NAME']};"
#                 f"UID={db_settings['USER']};"
#                 f"PWD={db_settings['PASSWORD']};"
#             )
from django.shortcuts import render, redirect
from .forms import SearchForm
from django.conf import settings
import pyodbc
import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from information.employment_info.models import Financial





def search_input(request):
    results = []
    selected_fields = []
    if request.method == 'POST':
        form = SearchForm(request.POST)
        selected_fields = request.POST.getlist("fields") or ["First_name", "Last_name"]

        if form.is_valid():
            db_settings = settings.DATABASES['default']

            # اتصال با SQL Authentication (بر اساس settings.py)
            conn_str = (
                            f"DRIVER={db_settings['OPTIONS']['driver']};"
                            f"SERVER={db_settings['HOST']},{db_settings['PORT']};"
                            f"DATABASE={db_settings['NAME']};"
                            f"UID={db_settings['USER']};"
                            f"PWD={db_settings['PASSWORD']};"
                        )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            all_columns = {
                "First_name": "p.First_name",
                "Last_name": "p.Last_name",
                "Father_name": "p.Father_name",
                "National_code": "p.National_code",
                "Birth_name": "p.Birth_name",
                "Birth_date": "p.Birth_date",
                "Birth_city": "p.Birth_city",
                "Adress": "p.Adress",
                "Phone_number": "ph.Phone_number",
                "Mobile_number": "ph.Mobile_number",
                "Gender_status": "p.Gender_status",
                "Marital_status": "p.Marital_status",
                "ChildCount": "COALESCE(f.ChildCount,0)",
                "Employment_id": "o.Employment_id",
                "Activity_type": "a.Activity_type",
                "Payment_type": "pe.Payment_type",
                "Current_job": "cj.Current_job",
                "Job_relation": "jr.Job_relation",
                "Job_title": "jt.Job_title",
                "Job_unit": "ju.Job_unit",
                "Levels": "jl.Levels",
                "Hire_status": "hs.Hire_status",
                "Salary_base": "f.Salary_base",
                "Insurance_type": "it.Insurance_type",
                "Account_Melli": "Account_Melli",
                "Account_Jamjam": "Account_Jamjam",
                "Sheba_number": "acc.Sheba_number",
                "Hire_date": "o.Hire_date",
                "Retirement_date": "o.Retirement_date",
                "End_date_cooperation": "o.End_date_cooperation",
                "Isargari": "o.Isargari",
                "Mandatory_hours": "ma.Mandatory_hours",
                "Field_study": "ed.Field_study",
                "Educational_level": "el.Educational_level",
            }

            selected_sql_columns = [all_columns[field] for field in selected_fields if field in all_columns]

            query = """EXEC Sp_Search ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"""

            def clean_param(val, expected_type=None):
                if val in [None, '', False]:
                    return None
                try:
                    if expected_type in ['int', 'bigint']:
                        return int(val)
                    return str(val).strip()
                except (ValueError, TypeError):
                    return None

            params = [
                clean_param(form.cleaned_data.get('name')),
                clean_param(form.cleaned_data.get('family')),
                clean_param(form.cleaned_data.get('father_name')),
                clean_param(form.cleaned_data.get('national_code')),
                clean_param(form.cleaned_data.get('birth_number')),
                clean_param(form.cleaned_data.get('birth_date')),
                clean_param(form.cleaned_data.get('birth_city')),
                clean_param(form.cleaned_data.get('employment_id')),
                clean_param(form.cleaned_data.get('gender')),
                clean_param(form.cleaned_data.get('marital_status')),
                clean_param(form.cleaned_data.get('children_num'), 'int'),
                clean_param(form.cleaned_data.get('salary_base'), 'bigint'),
                clean_param(form.cleaned_data.get('id_personal'), 'int'),
                clean_param(form.cleaned_data.get('activity_type')),
                clean_param(form.cleaned_data.get('payment_type')),
                clean_param(form.cleaned_data.get('job_level')),
                clean_param(form.cleaned_data.get('current_job')),
                clean_param(form.cleaned_data.get('hire_status')),
                clean_param(form.cleaned_data.get('job_relation')),
                clean_param(form.cleaned_data.get('job_title')),
                clean_param(form.cleaned_data.get('job_unit')),
                clean_param(form.cleaned_data.get('insurance_type')),
                clean_param(form.cleaned_data.get('bank')),
                clean_param(form.cleaned_data.get('sheba_number')),
                clean_param(form.cleaned_data.get('account_melli')),
                clean_param(form.cleaned_data.get('end_date_cooperation')),
                clean_param(form.cleaned_data.get('hire_date')),
                clean_param(form.cleaned_data.get('retirement_date')),
                clean_param(form.cleaned_data.get('isargari'), 'bit'),
                clean_param(form.cleaned_data.get('mandatory_hours')),
                clean_param(form.cleaned_data.get('address')),
                clean_param(form.cleaned_data.get('phone_number')),
                clean_param(form.cleaned_data.get('mobile_number')),
                clean_param(form.cleaned_data.get('educational_level')),
                clean_param(form.cleaned_data.get('field_study')),
                clean_param(form.cleaned_data.get('account_jamjam')),
            ]
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            final_row = cursor.fetchall()
            if not final_row:
                messages.error(request, 'هیچ نتیجه‌ای یافت نشد')
                # print('noooo')
                return redirect('information:search:search')
            else:
                for row in final_row:
                    row_dict = {col: (val if val is not None else '') for col, val in zip(columns, row)}
                    # محاسبه حقوق حکم برای هر رکورد(salary_base = حقوق حکم)
                    try:
                        financial = Financial.objects.get(id_personal=row_dict.get('Id_personal'))
                        y = sum([
                            financial.salary_base or 0,
                            financial.management_right or 0,
                            financial.f_51 or 0,
                            financial.f_abohava or 0,
                            financial.f_isargari or 0,
                            financial.f_mahroomiat or 0,
                            financial.f_resaneh or 0,
                            financial.f_sakhti_kar or 0,
                            financial.f_shoghl or 0
                        ])
                    except Financial.DoesNotExist:
                        y = 0

                    # جایگزینی مقدار Salary_base با y
                    row_dict['Salary_base'] = y

                    results.append(row_dict)

                cursor.close()
                conn.close()

                request.session['excel_results'] = results
                request.session['excel_selected_fields'] = selected_fields
                form = SearchForm()
        else:
            form = SearchForm()
    else:
        form = SearchForm()  # ✅ برای حالت GET

    return render(
        request,
        'main/includes/search/search.html',
        {
            'form': form,
            'results': results,
            'selected_fields': selected_fields,
        }
    )

def export_to_excel_view(request):
    results = request.session.get('excel_results')
    selected_fields = request.session.get('excel_selected_fields')

    if not results or not selected_fields:
        return HttpResponse("داده‌ای برای خروجی یافت نشد.", status=400)

    df = pd.DataFrame(results)

    df = df[selected_fields]

    column_names = {
        "First_name": "نام",
        "Last_name": "نام خانوادگی",
        "Father_name": "نام پدر",
        "National_code": "کد ملی",
        "Birth_number":"شماره شناسنامه",
        "Birth_date": "تاریخ تولد",
        "Birth_city": "محل تولد",
        "Address": " آدرس",
        "Phone_number": " تلفن",
        "Mobile_number": " همراه",
        "Gender_status": "جنسیت",
        "Marital_status": "وضعیت تأهل",
        "ChildCount": "تعداد فرزندان",
        "Field_study": "رشته تحصیلی",
        "Educational_level": "سطح تحصیلات",
        "Employment_id": "شماره کارمندی",
        "Activity_type": "نوع فعالیت",
        "Payment_type": "نوع پرداخت",
        "Current_job": "شغل فعلی",
        "Job_relation": "رابطه شغلی",
        "Job_title": "عنوان شغلی",
        "Job_unit": "واحد خدمتی",
        "Levels": "رده شغلی",
        "Hire_status": "نوع استخدام",
        "Mandatory_hours": "ساعت موظف",
        "Hire_date": "تاریخ استخدام",
        "Retirement_date": "تاریخ بازنشستگی",
        "End_date_cooperation": "تاریخ قطع همکاری",
        "Salary_base": "حقوق حکم",
        "Insurance_type": "نوع بیمه",
        "Account_Melli": "شماره حساب ملی",
        "Account_Jamjam": "شماره حساب جام جم",
        "Sheba_number": "شماره شبا",
        "Isargari": "ایثارگری",
    }

    df.rename(columns=column_names, inplace=True)

    response: HttpResponse = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=search_results.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='نتایج جستجو')

    return response