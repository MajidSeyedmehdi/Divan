from django.shortcuts import render
from django.contrib import messages
from .forms import PersonallyForm, FamilyForm, OfficialForm, FinancialForm, PermisionsForm
from .models import (Personally, Location, Education, Phone, Family, Educational_level, Official, JobUnit, JobTitle,
                     CurrentJob, HireStatus, JobRelation, Financial, Levels, Activity_Type, Accounting, Payment_Type,
                     Insurance_Type, Bank, Mandatory_Hours, OfficialHire, Formula,
                     OfficialActivity, OfficialPaymentType, OfficialJobRelation, OfficialJobUnit, Permisions)

def employment_info_view(request):
    context = {
        'personal_form': PersonallyForm(),
        'family_form': FamilyForm(),
        'official_form': OfficialForm(),
        'financial_form': FinancialForm(),
        'prefilled_data': {},
        'tab': 'personal',
        'educational_levels': Educational_level.objects.filter(active=True, del_field=False),
        'job_units': JobUnit.objects.filter(active=True, del_field=False),
        'job_titles': JobTitle.objects.filter(active=True, del_field=False),
        'current_jobs': CurrentJob.objects.filter(active=True, del_field=False),
        'hire_statuses': HireStatus.objects.filter(active=True, del_field=False),
        'job_relations': JobRelation.objects.filter(active=True, del_field=False),
        'job_levels': Levels.objects.filter(active=True, del_field=False),
        'levels': Levels.objects.filter(active=True, del_field=False),
        'activity_type': Activity_Type.objects.filter(active=True, del_field=False),
        'payment_type': Payment_Type.objects.filter(active=True, del_field=False),

        'insurance_type': Insurance_Type.objects.filter(active=True, del_field=False),
        'mandatory_Hours': Mandatory_Hours.objects.filter(active=True, del_field=False),
        'bank': Bank.objects.filter(active=True, del_field=False),
        'officialActivity': OfficialActivity.objects.filter(active=True, del_field=False),
        'officialPaymentType': OfficialPaymentType.objects.filter(active=True, del_field=False),
        'officialJobRelation': OfficialJobRelation.objects.filter(active=True, del_field=False),
        'officialHire': OfficialHire.objects.filter(active=True, del_field=False),
        'officialJobUnit': OfficialJobUnit.objects.filter(active=True, del_field=False),
        'formula': Formula.objects.filter(active=True, del_field=False),
    }

    def fill_prefilled_data(person):
        prefilled = {
            'first_name': person.first_name,
            'last_name': person.last_name,
            'father_name': person.father_name,
            'birth_number': person.birth_number,
            'gender_status': person.gender_status,
            'marital_status': person.marital_status,
            'national_code': person.national_code,
            'birth_date': person.birth_date,
            'birth_city': person.birth_city,
            'email': person.email,
            'id_personal': person.id_personal,
        }
        official = Official.objects.filter(id_personal=person).first()
        if official:
            prefilled.update({
                'id_official': official.id_official,
                'employment_id': official.employment_id,
                'id_job_title': official.id_job_title_id if official.id_job_title else None,
                'id_job_unit': official.id_job_unit_id if official.id_job_unit else None,
                'id_job_level': official.id_job_level_id if official.id_job_level else None,
                'id_current_job': official.id_current_job_id if official.id_current_job else None,
                'id_current_job_level': official.id_current_job_level_id if official.id_current_job_level else None,
                'id_hire_status': official.id_hire_status_id if official.id_hire_status else None,
                'id_job_relation': official.id_job_relation_id if official.id_job_relation else None,
                'id_mandatory_hours': official.id_mandatory_hours_id if official.id_mandatory_hours else None,
                'id_activity_type': official.id_activity_type_id if official.id_activity_type else None,
                'id_payment_type': official.id_payment_type_id if official.id_payment_type else None,
                'hire_date': official.hire_date,
                'last_promotion_date': official.last_promotion_date,
                'programming_code': official.programming_code,
                'retirement_date': official.retirement_date,
                'end_date_cooperation': official.end_date_cooperation,
                'isargari': official.isargari,
                'basij': official.basij,

            })
        permisions = Permisions.objects.filter(id_personal=person).first()
        if permisions:
            prefilled.update({
                'id_permision': permisions.id_permision,
                # 'id_official': permisions.id_official,
                'permision_studio': permisions.permision_studio,
                'permision_fanni_pakhsh': permisions.permision_fanni_pakhsh,
                'permision_reportaj': permisions.permision_reportaj,
                'permision_15_khordad': permisions.permision_15_khordad,
                'permision_fanni_poshtibani': permisions.permision_fanni_poshtibani,
                'permision_sound_recorders': permisions.permision_sound_recorders,
            })
        financial = Financial.objects.filter(id_personal=person).first()
        if financial:
            prefilled.update({
                'id_financial': financial.id_financial,
                'salary_base' : financial.salary_base,
                'id_insurance_type': financial.id_insurance_type_id if financial.id_insurance_type else None,
                'insurance_number': financial.insurance_number,
                'housing_right': financial.housing_right,
                'children_right': financial.children_right,
                'wife_right': financial.wife_right,
                'kharobar': financial.kharobar,
                'sanavat': financial.sanavat,
                'eydi': financial.eydi,
                'f_shoghl': financial.f_shoghl,
                'f_amoozesh' : financial.f_amoozesh,
                'f_mohandesi': financial.f_mohandesi,
                'f_abohava': financial.f_abohava,
                'f_mahroomiat': financial.f_mahroomiat,
                'f_isargari': financial.f_isargari,
                'f_51': financial.f_51,
                'f_sakhti_kar': financial.f_sakhti_kar,
                # 'f_marzi': financial.f_marzi,
                # 'f_enteghal': financial.f_enteghal,
                # 'f_jazb_mahroom': financial.f_jazb_mahroom,
                'management_right': financial.management_right,
                'f_resaneh': financial.f_resaneh,
            })
            # محاسبه مجموع فوق العاده ها و پایه حقوق
            financial_fields = [
                'salary_base',
                'f_shoghl', 'f_mohandesi','f_amoozesh' , 'f_abohava', 'f_mahroomiat', 'f_isargari', 'f_51',
                'f_sakhti_kar', 'management_right', 'f_resaneh'
            ]
            total_financial = sum(getattr(financial, field, 0) or 0 for field in financial_fields)
            prefilled['total_financial'] = total_financial
            baravord = total_financial - (getattr(financial, 'f_mohandesi', 0) or 0)
            prefilled['baravord'] = baravord

            # Load bank account information
            accounting = Accounting.objects.filter(id_financial=financial, active=True, del_field=False).first()
            if accounting:
                prefilled.update({
                    'id_bank': accounting.id_bank_id,
                    'account_number': accounting.account_number,
                    'sheba_number': accounting.sheba_number,
                })
        return prefilled

    def reload_person_data(person, context):
        """Reload all person data after save operations"""
        if person:
            context['prefilled_data'] = fill_prefilled_data(person)
            # Education info
            education = Education.objects.filter(id_personal=person).first()
            if education:
                context['prefilled_data']['field_study'] = education.field_study
                context['prefilled_data']['educational_level'] = education.id_educational_level_id
                context['prefilled_data']['university'] = education.university
            # Contact & Address info
            location = Location.objects.filter(id_personal=person).first()
            if location:
                context['prefilled_data']['postal_code'] = location.postal_code
                context['prefilled_data']['city'] = location.city
                context['prefilled_data']['address'] = location.address
            phone = Phone.objects.filter(id_personal=person).first()
            if phone:
                context['prefilled_data']['mobile_number'] = phone.mobile_number
                context['prefilled_data']['phone_number'] = phone.phone_number
            # Family info
            family_list = list(Family.objects.filter(id_personal=person, active=True, del_field=False))
            context['family_list'] = family_list
            if family_list:
                family = family_list[0]
                context['prefilled_data']['family_first_name'] = family.first_name
                context['prefilled_data']['family_last_name'] = family.last_name
                context['prefilled_data']['family_national_code'] = family.national_code
                context['prefilled_data']['family_birth_date'] = family.birth_date
                context['prefilled_data']['family_type'] = family.type
            # Bank accounts info
            bank_accounts = Accounting.objects.filter(id_financial__id_personal=person, active=True, del_field=False)
            context['bank_accounts'] = bank_accounts
            context['personal_form'] = PersonallyForm(initial=context['prefilled_data'])
            context['family_form'] = FamilyForm(initial=context['prefilled_data'])
            context['official_form'] = OfficialForm(initial=context['prefilled_data'])
            context['financial_form'] = FinancialForm(initial=context['prefilled_data'])

    if request.method == 'POST':
        id_personal = request.POST.get('id_personal')
        person = Personally.objects.filter(id_personal=id_personal).first() if id_personal else None

        # Soft delete a family row: set active=False, del_field=True
        if 'delete_family_member' in request.POST:
            family_id = request.POST.get('delete_family_member')
            family = Family.objects.filter(id_family=family_id).first()
            if family:
                try:
                    family.active = False
                    family.del_field = True
                    family.save(update_fields=['active', 'del_field'])
                    messages.success(request, 'عضو خانواده با موفقیت حذف شد.')
                    # After deletion, reload lists for the same person
                    person = family.id_personal
                    reload_person_data(person, context)
                except Exception as e:
                    messages.error(request, f'خطا در حذف عضو خانواده: {e}')
            else:
                messages.error(request, 'عضو خانواده یافت نشد.')
            context['tab'] = 'family'
            return render(request, 'main/includes/employment_info/employment_info.html', context)

        if 'select_family_member' in request.POST:
            # User clicked a family member in the table
            family_id = request.POST.get('select_family_member')
            family = Family.objects.filter(id_family=family_id).first()
            if family:
                context['prefilled_data'] = fill_prefilled_data(family.id_personal)
                context['prefilled_data']['family_first_name'] = family.first_name
                context['prefilled_data']['family_last_name'] = family.last_name
                context['prefilled_data']['family_national_code'] = family.national_code
                context['prefilled_data']['family_birth_date'] = family.birth_date
                context['prefilled_data']['family_type'] = family.type
                context['prefilled_data']['family_id'] = family.id_family
            # Always reload family list
            person = family.id_personal if family else person
            family_list = list(Family.objects.filter(id_personal=person, active=True, del_field=False)) if person else []
            context['family_list'] = family_list
            context['tab'] = 'family'
            return render(request, 'main/includes/employment_info/employment_info.html', context)

        if 'search_national_code' in request.POST:
            code = request.POST.get('national_code')
            person = Personally.objects.filter(national_code=code).first()
            if person:
                context['prefilled_data'] = fill_prefilled_data(person)
                context['tab'] = 'personal'
                # Education info
                education = Education.objects.filter(id_personal=person).first()
                if education:
                    context['prefilled_data']['field_study'] = education.field_study
                    context['prefilled_data']['educational_level'] = education.id_educational_level_id
                    context['prefilled_data']['university'] = education.university
                # Contact & Address info
                location = Location.objects.filter(id_personal=person).first()
                if location:
                    context['prefilled_data']['postal_code'] = location.postal_code
                    context['prefilled_data']['city'] = location.city
                    context['prefilled_data']['address'] = location.address
                phone = Phone.objects.filter(id_personal=person).first()
                if phone:
                    context['prefilled_data']['mobile_number'] = phone.mobile_number
                    context['prefilled_data']['phone_number'] = phone.phone_number
                family_list = list(Family.objects.filter(id_personal=person, active=True, del_field=False))
                context['family_list'] = family_list
                if family_list:
                    family = family_list[0]
                    context['prefilled_data']['family_first_name'] = family.first_name
                    context['prefilled_data']['family_last_name'] = family.last_name
                    context['prefilled_data']['family_national_code'] = family.national_code
                    context['prefilled_data']['family_birth_date'] = family.birth_date
                    context['prefilled_data']['family_type'] = family.type
                # Bank accounts info
                bank_accounts = Accounting.objects.filter(id_financial__id_personal=person, active=True,
                                                          del_field=False)
                context['bank_accounts'] = bank_accounts
                messages.success(request, 'کارمند یافت شد و اطلاعات بارگذاری شد.')
            else:
                messages.error(request, 'کد ملی یافت نشد.')

        elif 'save_personal' in request.POST:
            form = PersonallyForm(request.POST)
            context['personal_form'] = form
            if form.is_valid():
                code = form.cleaned_data['national_code']
                person = Personally.objects.filter(national_code=code).first()
                extra_data = {
                    'postal_code': request.POST.get('postal_code'),
                    'city': request.POST.get('city'),
                    'address': request.POST.get('address'),
                    'field_study': request.POST.get('field_study'),
                    'educational_level': request.POST.get('educational_level'),
                    'university': request.POST.get('university'),
                    'mobile_number': request.POST.get('mobile_number'),
                    'phone_number': request.POST.get('phone_number'),
                }
                if person:
                    form.save_sp(request.user, update=True, id_personal=person.id_personal, extra_data=extra_data)
                    messages.success(request, 'اطلاعات شخصی با موفقیت به‌روزرسانی شد.')
                else:
                    form.save_sp(request.user, update=False, extra_data=extra_data)
                    messages.success(request, 'ثبت موفقیت‌آمیز بود.')
                
                # Reload person data after saving
                person = Personally.objects.filter(national_code=code).first()
                reload_person_data(person, context)
                context['tab'] = 'personal'
            else:
                print(form.errors)
                messages.error(request, 'خطا در اعتبارسنجی فرم.')
                context['tab'] = 'personal'

        elif 'save_family' in request.POST:
            id_family = request.POST.get('id_family')
            family_form = FamilyForm(request.POST)
            context['family_form'] = family_form
            if family_form.is_valid() and id_personal:
                try:
                    family_form.save_sp(request.user, update=bool(id_family), id_personal=id_personal, id_family=id_family)
                    messages.success(request, 'اطلاعات خانوادگی با موفقیت ثبت شد.')
                    # Reload person data after saving
                    person = Personally.objects.filter(id_personal=id_personal).first()
                    reload_person_data(person, context)
                except Exception as e:
                    messages.error(request, f'خطا در ثبت اطلاعات خانوادگی: {e}')
                context['tab'] = 'family'
            else:
                messages.error(request, 'خطا در اعتبارسنجی فرم خانوادگی.')
                context['tab'] = 'family'

        elif 'save_official' in request.POST:
            id_official = request.POST.get('id_official')
            official_form = OfficialForm(request.POST)
            context['official_form'] = official_form
            if official_form.is_valid() and id_personal:
                try:
                    official_form.save_sp(request.user, id_personal=id_personal, id_official=id_official)
                    messages.success(request, 'اطلاعات اداری با موفقیت ثبت/ویرایش شد.')
                    # Reload person data after saving
                    person = Personally.objects.filter(id_personal=id_personal).first()
                    reload_person_data(person, context)
                    # Re-initialize forms with updated data
                    context['personal_form'] = PersonallyForm(initial=context['prefilled_data'])
                    context['family_form'] = FamilyForm(initial=context['prefilled_data'])
                    context['official_form'] = OfficialForm(initial=context['prefilled_data'])
                    context['financial_form'] = FinancialForm(initial=context['prefilled_data'])
                    context['permisions_form'] = PermisionsForm(initial=context['prefilled_data'])
                except Exception as e:
                    messages.error(request, f'خطا در ثبت اطلاعات اداری: {e}')
                context['tab'] = 'official'
            else:
                if not official_form.is_valid():
                    messages.error(request, official_form.errors)
                    messages.error(request, 'خطا در اعتبارسنجی فرم اداری.')
                context['tab'] = 'official'
        elif 'save_permisions' in request.POST:
            id_permision = request.POST.get('id_permision')
            permisions_form = PermisionsForm(request.POST)
            context['permisions_form'] = permisions_form
            if permisions_form.is_valid() and id_personal:
                try:
                    result=permisions_form.save_sp(request.user, id_personal=id_personal , id_permision=id_permision)
                    messages.success(request, 'اطلاعات مجوزها با موفقیت ثبت/ویرایش شد.')
                    person = Personally.objects.filter(id_personal=id_personal).first()
                    reload_person_data(person, context)
                    # Re-initialize forms with updated data
                    context['personal_form'] = PersonallyForm(initial=context['prefilled_data'])
                    context['family_form'] = FamilyForm(initial=context['prefilled_data'])
                    context['official_form'] = OfficialForm(initial=context['prefilled_data'])
                    context['financial_form'] = FinancialForm(initial=context['prefilled_data'])
                    context['permisions_form'] = PermisionsForm(initial=context['prefilled_data'])
                except Exception as e:
                    messages.error(request, f'خطا در ثبت اطلاعات مجوزها: {e}')
                context['tab'] = 'permisions'
            else:
                if not permisions_form.is_valid():
                    messages.error(request, permisions_form.errors)
                    messages.error(request, 'خطا در اعتبارسنجی فرم مجوزها.')
                context['tab'] = 'permisions'

        elif 'save_financial' in request.POST:
            id_financial = request.POST.get('id_financial')
            financial_form = FinancialForm(request.POST)
            context['financial_form'] = financial_form
            if financial_form.is_valid() and id_personal:
                try:
                    result=financial_form.save_sp(request.user, id_personal=id_personal, id_financial=id_financial)
                    messages.success(request, 'اطلاعات مالی با موفقیت ثبت/ویرایش شد.')
                    # Reload person data after saving
                    person = Personally.objects.filter(id_personal=id_personal).first()
                    reload_person_data(person, context)
                    # Re-initialize forms with updated data
                    context['personal_form'] = PersonallyForm(initial=context['prefilled_data'])
                    context['family_form'] = FamilyForm(initial=context['prefilled_data'])
                    context['official_form'] = OfficialForm(initial=context['prefilled_data'])
                    context['financial_form'] = FinancialForm(initial=context['prefilled_data'])
                    context['permisions_form'] = PermisionsForm(initial=context['prefilled_data'])
                except Exception as e:
                    messages.error(request, f'خطا در ثبت اطلاعات مالی: {e}')
                context['tab'] = 'financial'
            else:
                if not financial_form.is_valid():
                    messages.error(request, financial_form.errors)
                    messages.error(request, 'خطا در اعتبارسنجی فرم مالی.')
                context['tab'] = 'financial'

        elif 'new_family_member' in request.POST:
            # User clicked 'عضو خانواده جدید' button: clear only family fields, keep other tabs' data, and ensure no id_family is present
            if person:
                context['prefilled_data'] = fill_prefilled_data(person)
            context['prefilled_data']['family_first_name'] = ''
            context['prefilled_data']['family_last_name'] = ''
            context['prefilled_data']['family_national_code'] = ''
            context['prefilled_data']['family_birth_date'] = ''
            context['prefilled_data']['family_type'] = ''
            # Do NOT set any id_family in context or form
            family_list = list(Family.objects.filter(id_personal=person, active=True, del_field=False)) if person else []
            context['family_list'] = family_list
            context['tab'] = 'family'
            return render(request, 'main/includes/employment_info/employment_info.html', context)
        elif 'select_bank_account' in request.POST:

            account_id = request.POST.get('select_bank_account')
            account = Accounting.objects.select_related('id_bank', 'id_financial__id_personal').filter(id_account=account_id).first()

            if account:
                person = account.id_financial.id_personal  # از طریق حساب مالی به شخص دسترسی پیدا کن
                context['prefilled_data'] = fill_prefilled_data(person)
                context['prefilled_data']['account_id'] = account.id_account
                context['prefilled_data']['account_number'] = account.account_number
                context['prefilled_data']['sheba_number'] = account.sheba_number
                context['prefilled_data']['id_bank'] = account.id_bank.id_bank
                context['bank_accounts'] = Accounting.objects.filter(id_financial__id_personal=person, active=True,del_field=False)
                context['financial_form'] = FinancialForm(initial=context['prefilled_data'])
            context['tab'] = 'financial'
        elif 'new_bank_account' in request.POST:
            if person:
                context['prefilled_data'] = fill_prefilled_data(person)

                financial = Financial.objects.filter(id_personal=person).first()
                if financial:
                    bank_accounts = Accounting.objects.filter(id_financial=financial, active=True, del_field=False)
                    context['bank_accounts'] = list(bank_accounts)
                else:
                    context['bank_accounts'] = []
            else:
                context['prefilled_data'] = {}
                context['bank_accounts'] = []

            context['prefilled_data']['account_number'] = ''
            context['prefilled_data']['sheba_number'] = ''
            context['prefilled_data']['id_bank'] = ''
            context['tab'] = 'financial'
            return render(request, 'main/includes/employment_info/employment_info.html', context)



    return render(request, 'main/includes/employment_info/employment_info.html', context)
