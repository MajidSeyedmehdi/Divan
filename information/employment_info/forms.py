import sys

from django import forms
from django.contrib.auth.models import Permission
from django.db import connection

from .models import Personally, Family, Official, Financial, Bank , Permisions

sys.stdout.reconfigure(encoding='utf-8')

class CommaSeparatedIntegerField(forms.CharField):
    def clean(self, value):
        value = super().clean(value)
        value = value.replace(',', '')
        if not value.isdigit():
            raise forms.ValidationError("عدد معتبر نیست.")
        return int(value)
class NationalCodeValidator:
    def __call__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise forms.ValidationError('کد ملی باید ۱۰ رقم باشد.')


class PersonallyForm(forms.ModelForm):
    national_code = forms.CharField(validators=[NationalCodeValidator()])

    class Meta:
        model = Personally
        fields = [
            'first_name', 'last_name', 'father_name', 'birth_number',
            'gender_status', 'marital_status', 'national_code',
            'birth_date', 'birth_city', 'email'
        ]

    def save_sp(self, user, update=False, id_personal=None, extra_data=None):
        
        code = self.cleaned_data['national_code']
        person = Personally.objects.filter(national_code=code).first()
        with connection.cursor() as cursor:
            if person:
                # UPDATE
                cursor.execute("""
                    EXEC Sp_UpdatePersonalInformation
                        @id_personal=%s, @first_name=%s, @last_name=%s, @father_name=%s, @birth_number=%s, @national_code=%s,
                        @birth_date=%s, @birth_city=%s, @gender_status=%s, @marital_status=%s, @email=%s, @personal_user_name=%s,
                        @postal_code=%s, @city=%s, @address=%s, @location_user_name=%s,
                        @educational_level=%s, @field_study=%s, @university=%s, @education_user_name=%s,
                        @phone_number=%s, @mobile_number=%s, @phone_user_name=%s
                """,[
                    person.id_personal,
                    self.cleaned_data['first_name'],
                    self.cleaned_data['last_name'],
                    self.cleaned_data['father_name'],
                    self.cleaned_data['birth_number'],
                    self.cleaned_data['national_code'],
                    self.cleaned_data['birth_date'],
                    self.cleaned_data['birth_city'],
                    self.cleaned_data['gender_status'],
                    self.cleaned_data['marital_status'],
                    self.cleaned_data['email'],
                    user.username,
                    extra_data.get('postal_code'),
                    extra_data.get('city'),
                    extra_data.get('address'),
                    user.username,
                    extra_data.get('educational_level'),
                    extra_data.get('field_study'),
                    extra_data.get('university'),
                    user.username,
                    extra_data.get('phone_number'),
                    extra_data.get('mobile_number'),
                    user.username
                ])
            else:
                # INSERT
                cursor.execute("""
                    EXEC Sp_InsertPersonalInformation
                        @first_name=%s, @last_name=%s, @father_name=%s, @birth_number=%s, @national_code=%s,
                        @birth_date=%s, @birth_city=%s, @gender_status=%s, @marital_status=%s, @email=%s, @personal_user_name=%s,
                        @postal_code=%s, @city=%s, @address=%s, @location_user_name=%s,
                        @field_study=%s, @educational_level=%s, @university=%s, @education_user_name=%s,
                        @mobile_number=%s, @phone_number=%s, @phone_user_name=%s
                """,[
                    self.cleaned_data['first_name'],
                    self.cleaned_data['last_name'],
                    self.cleaned_data['father_name'],
                    self.cleaned_data['birth_number'],
                    self.cleaned_data['national_code'],
                    self.cleaned_data['birth_date'],
                    self.cleaned_data['birth_city'],
                    self.cleaned_data['gender_status'],
                    self.cleaned_data['marital_status'],
                    self.cleaned_data['email'],
                    user.username,
                    extra_data.get('postal_code'),
                    extra_data.get('city'),
                    extra_data.get('address'),
                    user.username,
                    extra_data.get('field_study'),
                    extra_data.get('educational_level'),
                    extra_data.get('university'),
                    user.username,
                    extra_data.get('mobile_number'),
                    extra_data.get('phone_number'),
                    user.username
                ])
            result = cursor.fetchone()
            if result and (('ErrorMessage' in result) or (isinstance(result, dict) and result.get('ErrorMessage')) or (isinstance(result, tuple) and any('Error' in str(x) for x in result if x))):
                raise forms.ValidationError(result)
            return result



class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['first_name', 'last_name', 'national_code', 'birth_date', 'type']

    def save_sp(self, user, update=False, id_personal=None, id_family=None):
        with connection.cursor() as cursor:
            # Use the unified stored procedure that handles both insert and update
            cursor.execute("""
                EXEC Sp_UpdateFamilyInformation
                    @id_family=%s,
                    @id_personal=%s,
                    @type=%s,
                    @first_name=%s, @last_name=%s, @national_code=%s,
                    @birth_date=%s, @user_name=%s
            """, [
                id_family,
                id_personal,
                self.cleaned_data['type'],
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name'],
                self.cleaned_data['national_code'],
                self.cleaned_data['birth_date'],
                user.username
            ])
            result = cursor.fetchone()
            if result and (
                    ('ErrorMessage' in result) or (isinstance(result, dict) and result.get('ErrorMessage')) or (
                    isinstance(result, tuple) and any('Error' in str(x) for x in result if x))):
                raise forms.ValidationError(result)
            return result

class OfficialForm(forms.ModelForm):

    class Meta:
        model = Official
        fields = [
            'employment_id', 'id_activity_type', 'id_payment_type', 'isargari', 'basij',
            'id_job_unit', 'id_job_title', 'id_job_level', 'id_current_job', 'id_current_job_level', 'id_hire_status',
            'id_job_relation', 'id_mandatory_hours','hire_date', 'last_promotion_date', 'programming_code', 'retirement_date',
            'end_date_cooperation'
        ]


    def save_sp(self, user,update=False, id_personal=None, id_official=None):
        id_official = id_official if id_official not in [None, '', '0'] else None
        
        with connection.cursor() as cursor:
            params = [
                id_official,
                id_personal,
                self.cleaned_data['employment_id'],
                self.cleaned_data['id_activity_type'].id_activity_type if self.cleaned_data[
                    'id_activity_type'] else None,
                self.cleaned_data['id_payment_type'].id_payment_type if self.cleaned_data[
                    'id_payment_type'] else None,
                int(self.cleaned_data.get('isargari', False)),
                int(self.cleaned_data.get('basij', False)),
                self.cleaned_data['id_job_unit'].id_job_unit if self.cleaned_data['id_job_unit'] else None,
                self.cleaned_data['id_job_title'].id_job_title if self.cleaned_data['id_job_title'] else None,
                self.cleaned_data['id_job_level'].id_levels if self.cleaned_data['id_job_level'] else None,
                self.cleaned_data['id_current_job'].id_current_job if self.cleaned_data['id_current_job'] else None,
                self.cleaned_data['id_current_job_level'].id_levels if self.cleaned_data[
                    'id_current_job_level'] else None,
                self.cleaned_data['id_hire_status'].id_hire_status if self.cleaned_data['id_hire_status'] else None,
                self.cleaned_data['id_job_relation'].id_job_relation if self.cleaned_data[
                    'id_job_relation'] else None,
                self.cleaned_data['id_mandatory_hours'].id_mandatory_hours if self.cleaned_data[
                    'id_mandatory_hours'] else None,
                self.cleaned_data['hire_date'],
                self.cleaned_data.get('last_promotion_date', ''),
                self.cleaned_data.get('programming_code', ''),
                self.cleaned_data.get('retirement_date', ''),
                self.cleaned_data.get('end_date_cooperation', ''),
                user.username,  # @official_user_name
                user.username,  # @job_unit_user_name
                user.username,  # @hire_user_name
                user.username,  # @activity_user_name
                user.username,  # @payment_type_user_name
                user.username,  # @job_relation_user_name
            ]
            
            cursor.execute("""
                EXEC Sp_UpdateOfficialInformation
                    @id_official=%s, @id_personal=%s, @employment_id=%s, @id_activity_type=%s, @id_payment_type=%s,
                    @isargari=%s, @basij=%s,
                    @id_job_unit=%s, @id_job_title=%s, @id_job_level=%s, @id_current_job=%s, @id_current_job_level=%s, @id_hire_status=%s, @id_job_relation=%s,
                    @id_mandatory_hours=%s,@hire_date=%s, @last_promotion_date=%s, @programming_code=%s,@retirement_date=%s, @end_date_cooperation=%s,
                    @official_user_name=%s, @job_unit_user_name=%s, @hire_user_name=%s, @activity_user_name=%s, @payment_type_user_name=%s, @job_relation_user_name=%s
            """, params)
            result = cursor.fetchone()
            
            if result and (('ErrorMessage' in result) or (isinstance(result, dict) and result.get('ErrorMessage')) or (isinstance(result, tuple) and any('Error' in str(x) for x in result if x))):
                raise forms.ValidationError(result)
            return result

class PermisionsForm(forms.ModelForm):
    class Meta:
        model = Permisions
        fields = [
            'permision_studio', 'permision_fanni_pakhsh', 'permision_reportaj','permision_15_khordad', 'permision_fanni_poshtibani', 'permision_sound_recorders'
        ]
        widgets = {
            'permision_studio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permision_fanni_pakhsh': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permision_reportaj': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permision_15_khordad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permision_fanni_poshtibani': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'permision_sound_recorders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save_sp(self, user, update=False, id_personal=None, id_permision=None):
        id_permision = id_permision if id_permision not in [None, '', '0'] else None
        print(self.cleaned_data)
        with connection.cursor() as cursor:
            params = [
                id_permision,
                id_personal,
                int(bool(self.cleaned_data.get('permision_studio'))),
                int(bool(self.cleaned_data.get('permision_fanni_pakhsh'))),
                int(bool(self.cleaned_data.get('permision_reportaj'))),
                int(bool(self.cleaned_data.get('permision_15_khordad'))),
                int(bool(self.cleaned_data.get('permision_fanni_poshtibani'))),
                int(bool(self.cleaned_data.get('permision_sound_recorders'))),
                user.username,  # @permision_user_name

            ]

            cursor.execute("""
                EXEC Sp_UpdatePermisionsInformation
                    @id_permision=%s, @id_personal=%s, @permision_studio=%s, @permision_fanni_pakhsh=%s, @permision_reportaj=%s,
                    @permision_15_khordad=%s, @permision_fanni_poshtibani=%s, @permision_sound_recorders=%s,  @permision_user_name=%s
            """, params)
            result = cursor.fetchone()

            if result and (('ErrorMessage' in result) or (isinstance(result, dict) and result.get('ErrorMessage')) or (
                    isinstance(result, tuple) and any('Error' in str(x) for x in result if x))):
                raise forms.ValidationError(result)
            return result


class FinancialForm(forms.ModelForm):
    id_financial = forms.IntegerField(required=False, widget=forms.HiddenInput())
    id_bank = forms.ModelChoiceField(
        queryset=Bank.objects.filter(active=True, del_field=False),
        required=False, label='بانک'
    )
    account_number = forms.CharField(required=False, label='شماره حساب')
    sheba_number = forms.CharField(required=False, label='شماره شبا')

    class Meta:
        model = Financial
        fields = [
            'id_financial',
            'salary_base', 'id_insurance_type', 'insurance_number', 'housing_right', 'children_right',
            'wife_right','kharobar', 'sanavat', 'eydi', 'f_shoghl','f_amoozesh',
            'f_mohandesi', 'f_abohava', 'f_mahroomiat', 'f_isargari', 'f_51','f_sakhti_kar' ,
            # 'f_marzi' ,'f_enteghal' , 'f_jazb_mahroom'
            'management_right' , 'f_resaneh'
        ]

    # def clean_salary_base(self):
    #     raw_value = self.data.get('salary_base', '0')  # استفاده از self.data به‌جای cleaned_data
    #     cleaned = raw_value.replace(',', '').strip()
    #     if not cleaned.isdigit():
    #         raise forms.ValidationError("لطفاً فقط عدد صحیح وارد کنید.")
    #     return int(cleaned)

    def save_sp(self, user,update=False, id_personal=None, id_financial=None):
        id_financial = id_financial if id_financial not in [None, '', '0'] else None

        with connection.cursor() as cursor:
            params = [
                id_financial,
                id_personal,
                self.cleaned_data.get('salary_base', 0),
                self.cleaned_data['id_insurance_type'].id_insurance_type if self.cleaned_data['id_insurance_type'] else None,
                self.cleaned_data['insurance_number'],
                self.cleaned_data.get('housing_right', 0),
                self.cleaned_data.get('children_right', 0),
                self.cleaned_data.get('wife_right', 0),
                self.cleaned_data.get('kharobar', 0),
                self.cleaned_data.get('sanavat', 0),
                self.cleaned_data.get('eydi', 0),
                self.cleaned_data.get('f_shoghl', 0),
                self.cleaned_data.get('f_amoozesh', 0),
                self.cleaned_data.get('f_mohandesi', 0),
                self.cleaned_data.get('f_abohava', 0),
                self.cleaned_data.get('f_mahroomiat', 0),
                self.cleaned_data.get('f_isargari', 0),
                self.cleaned_data.get('f_51', 0),
                self.cleaned_data.get('f_sakhti_kar', 0),
                # self.cleaned_data.get('f_marzi', 0),
                # self.cleaned_data.get('f_enteghal', 0),
                # self.cleaned_data.get('f_jazb_mahroom', 0),
                self.cleaned_data.get('management_right', 0),
                self.cleaned_data.get('f_resaneh', 0),
                user.username,

                self.cleaned_data.get('id_bank').id_bank if self.cleaned_data.get('id_bank') else None,
                self.cleaned_data.get('account_number'),
                self.cleaned_data.get('sheba_number'),
                user.username
            ]
            cursor.execute("""
                EXEC Sp_UpdateFinancialInformation
                    @id_financial=%s,@id_personal=%s, @salary_base=%s, @id_insurance_type=%s, @insurance_number=%s, @housing_right=%s, @children_right=%s,
                    @wife_right=%s,@kharobar=%s, @sanavat=%s, @eydi=%s, @f_shoghl=%s, @f_amoozesh=%s, @f_mohandesi=%s, @f_abohava=%s, @f_mahroomiat=%s, @f_isargari=%s, 
                    @f_51=%s, @f_sakhti_kar=%s, @management_right=%s, @f_resaneh=%s, @financial_user_name=%s,
                    @id_bank=%s,@account_number=%s,@sheba_number=%s,@accounting_user_name=%s
            """, params)
            result = cursor.fetchone()
            # اگر مقدار برگشتی یک عدد بود (id_financial جدید)، آن را برگردان
            if result and isinstance(result, tuple) and len(result) == 1 and isinstance(result[0], int):
                return result[0]
            # اگر پیام خطا یا موفقیت بود، همان را برگردان
            if result and (('ErrorMessage' in result) or (isinstance(result, dict) and result.get('ErrorMessage')) or (isinstance(result, tuple) and any('Error' in str(x) for x in result if x))):
                raise forms.ValidationError(result)
            return result