from django import forms
from .models import JobRelation, JobTitle, JobUnit

class SearchForm(forms.Form):
    name = forms.CharField(label='نام', required=False)
    family = forms.CharField(label='نام خانوادگی', required=False)
    national_code = forms.CharField(label='کد ملی', required=False)
    employment_id = forms.CharField(label='شماره کارمندی', required=False)
    marital_status = forms.ChoiceField(
        label='وضعیت تأهل',
        choices=[('S', 'مجرد'), ('M', 'متاهل'),('D', 'طلاق'),('W', 'فوت همسر')],
        widget=forms.RadioSelect,
        required=False
    )
    gender = forms.ChoiceField(
        label='جنسیت',
        choices=[('M', 'مرد'), ('F', 'زن')],
        widget=forms.RadioSelect,
        required=False
    )
    activity_type = forms.CharField(label='نوع فعالیت', required=False)
    payment_type = forms.CharField(label='نوع پرداخت', required=False)
    hire_status = forms.CharField(label='نوع استخدام', required=False)
    current_job = forms.CharField(label='شغل فعلی', required=False)
    job_level = forms.CharField(label='رده شغلی', required=False)
    job_title = forms.ChoiceField(label='عنوان شغلی', required=False)
    job_relation = forms.ChoiceField(label='نوع همکاری', required=False)
    job_unit = forms.ChoiceField(label=' واحد خدمتی', required=False)
    salary_base = forms.BooleanField(label='حقوق پایه', required=False)
    insurance_type = forms.BooleanField(label='نوع بیمه', required=False)
    bank = forms.BooleanField(label='بانک', required=False)
    account_number = forms.BooleanField(label='شماره حساب', required=False)
    sheba_number = forms.BooleanField(label='شماره شبا', required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        job_titles = JobTitle.objects.values_list('job_title', 'job_title').distinct()
        self.fields['job_title'].choices = [('', '---------')] + list(job_titles)

        job_relations = JobRelation.objects.values_list('job_relation', 'job_relation').distinct()
        self.fields['job_relation'].choices = [('', '---------')] + list(job_relations)

        job_unit = JobUnit.objects.values_list('job_unit', 'job_unit').distinct()
        self.fields['job_unit'].choices = [('', '---------')] + list(job_unit)