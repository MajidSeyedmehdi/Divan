from django.shortcuts import render, redirect
from .models import Financial, Official, FormulaSetting, Personal
from utils.db_connection import connect_db
from django.urls import reverse
from django.http import HttpResponse
import pandas as pd
import json
from django.core.paginator import Paginator



def salary_start_view(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'save_formula':
            hire_statuses = ['1', '3', '5', '6', '7', '8', '9', '11', '12', '13', '15']
            user_name = request.user.username or "system"
            # print("🔍:", Financial.objects.count())
            for hs in hire_statuses:
                formula_key = f'formula_{hs}'
                formula_value = request.POST.get(formula_key, '').strip()

                if formula_value:
                    # print("Sending to SP:", formula_value, hs, user_name)
                    with connect_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            EXEC Sp_InsertFormula 
                                @formula=?, 
                                @id_hire_status=?,
                                @user_name=?
                        """, [formula_value, int(hs), user_name])

            return render(request, "main/includes/setting/payment_calculation/setting.html", get_formulas_context())

        elif action == 'show_salary':
            return redirect(reverse('payment_calculation:salary_results'))

    return render(request, "main/includes/setting/payment_calculation/setting.html", get_formulas_context())


def get_formulas_context():
    hire_statuses = ['1', '3', '5', '6', '7', '8', '9', '11', '12', '13', '15']

    def get_formula(hs):
        obj = FormulaSetting.objects.filter(hire_status=hs).first()
        return obj.formula if obj else ''

    context = {
        'formula_rasmi_s': get_formula('1'),
        'formula_rasmi_t': get_formula('3'),
        'formula_peymani': get_formula('5'),
        'formula_gharardadi': get_formula('6'),
        'formula_kharid': get_formula('7'),
        'formula_sherkati': get_formula('8'),
        'formula_amrie': get_formula('9'),
        'formula_tabsare28': get_formula('11'),
        'formula_tabsare38': get_formula('12'),
        'formula_rade38': get_formula('13'),
        'formula_tabsare4': get_formula('15'),
    }
    return context


def salary_result_view(request):
    results = []
    records = Financial.objects.all()

    all_formula_statuses = list(FormulaSetting.objects.values_list('hire_status', flat=True))

    for record in records:
        try:
            y = sum([
                record.salary_base or 0,
                record.management_right or 0,
                record.f_51 or 0,
                record.f_abohava or 0,
                # record.f_enteghal or 0,
                record.f_isargari or 0,
                # record.f_jazb_mahroom or 0,
                record.f_mahroomiat or 0,
                # record.f_marzi or 0,
                record.f_resaneh or 0,
                record.f_sakhti_kar or 0,
                record.f_shoghl or 0
            ])

            personal = Personal.objects.filter(id_personal=record.id_personal).first()
            if not personal:
                raise ValueError("")

            official = Official.objects.filter(id_personal=record.id_personal).first()
            if not official:
                raise ValueError("")

            hire_status = official.hire_status

            try:
                hs_int = int(hire_status)
            except Exception as e:
                print("cannot convert hire_status to int:", e)
                hs_int = None

            formula_obj = None
            if hs_int is not None:
                formula_obj = FormulaSetting.objects.filter(hire_status=hs_int).first()

            if not formula_obj:
                raise ValueError(f"فرمولی برای وضعیت استخدامی {hire_status} یافت نشد")

            formula_text = formula_obj.formula.strip()

            hour_result = int(round(eval(formula_text, {"__builtins__": None}, {"y": y}), 0))

            salary_list = [
                record.sanavat,
                record.children_right,
                record.Housing_right,
                record.kharobar,
                record.wife_right,
            ]
            total_result = sum([float(i or 0) for i in salary_list])
            final_salary = y

            results.append({

                "national_code": personal.national_code,
                "first_name": personal.first_name,
                "last_name": personal.last_name,
                "job_relation": official.job_relation.title_job_rel if official.job_relation else "نامشخص",
                "job_title": official.job_title.title_job_ti if official.job_title else "نامشخص",
                "job_level": official.job_level.title_job_le if official.job_level else "نامشخص",
                "job_unit": official.job_unit.title_job_un if official.job_unit else "نامشخص",
                "salary_base": record.salary_base,
                "hour_salary": hour_result,
                "final_salary": final_salary,
            })

        except Exception as e:
            results.append({

                "national_code": personal.national_code if 'personal' in locals() and personal else "",
                "first_name": personal.first_name if 'personal' in locals() and personal else "",
                "last_name": personal.last_name if 'personal' in locals() and personal else "",
                "job_relation": official.job_relation if 'official' in locals() and official else "",
                "job_title": official.job_title if 'official' in locals() and official else "",
                "job_level": official.job_level if 'official' in locals() and official else "",
                "job_unit": official.job_unit if 'official' in locals() and official else "",
                "salary_base": record.salary_base,
                "hour_salary": "",
                "final_salary": "",
            })
    paginator = Paginator(results, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        # print(results)
    request.session['excel_results'] = results

    return render(request, "main/includes/setting/payment_calculation/salary_result.html", {
        "page_obj": page_obj,
        "results": results

    })


def export_to_excel(request):
    results = request.session.get('excel_results')

    if not results:
        return HttpResponse("اطلاعاتی برای خروجی اکسل پیدا نشد.", status=400)

    df = pd.DataFrame(results)

    # تغییر نام ستون‌ها به فارسی یا هر عنوان دلخواه
    column_names = {
        "national_code": "کد ملی",
        "first_name": "نام",
        "last_name": "نام خانوادگی",
        "job_relation": "نوع رابطه استخدامی",
        "job_title": "عنوان شغلی",
        "job_level": "سطح شغل",
        "job_unit": "واحد",
        "salary_base": "حقوق پایه",
        "hour_salary": "حقوق ساعتی",
        "final_salary": "حقوق حکم",
    }
    df.rename(columns=column_names, inplace=True)

    # ساخت فایل اکسل
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=salary_results.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='حقوق')

    return response
