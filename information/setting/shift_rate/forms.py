from django import forms
from information.employment_info.models import CurrentJob, Levels, JobLevels
from sound_recorders.models import Shift_Type, Shift
from django.db import connection


class ShiftRateFilterForm(forms.Form):
    """فرم فیلتر ساده نرخ شیفت"""

    def __init__(self, *args, **kwargs):
        # گرفتن مقادیر انتخاب شده قبلی
        selected_job_id = kwargs.pop('selected_job_id', None)
        selected_level_id = kwargs.pop('selected_level_id', None)
        selected_shift_type_id = kwargs.pop('selected_shift_type_id', None)
        selected_shift_name = kwargs.pop('selected_shift_name', None)

        super().__init__(*args, **kwargs)

        # --- ۱. شغل فعلی ---
        jobs = CurrentJob.objects.filter(
            active=True,
            del_field=False,
            is_seda=True
        ).order_by('current_job')

        job_choices = [("", "همه")]
        job_choices += [(str(j.id_current_job), j.current_job) for j in jobs]

        self.fields['job'] = forms.ChoiceField(
            choices=job_choices,
            label='شغل',
            initial=selected_job_id,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_job',
            })
        )

        # --- ۲. رده شغلی (وابسته به شغل) ---
        level_choices = [("", "همه")]

        if selected_job_id:
            # گرفتن رده‌های مربوط به این شغل از JobLevels
            level_ids = JobLevels.objects.filter(
                current_job_id=selected_job_id,
                active=True,
                del_field=False
            ).values_list('level_id', flat=True)

            # گرفتن اطلاعات کامل رده‌ها
            if level_ids:
                levels = Levels.objects.filter(
                    id_levels__in=level_ids,
                    active=True,
                    del_field=False
                ).order_by('levels')

                level_choices += [(str(l.id_levels), l.levels) for l in levels]

        self.fields['level'] = forms.ChoiceField(
            choices=level_choices,
            label='رده شغلی',
            initial=selected_level_id,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_level',
                'disabled': not bool(selected_job_id)
            })
        )

        # --- ۳. نوع شیفت ---
        shift_types = Shift_Type.objects.filter(
            active=True,
            del_field=False
        ).order_by('shift_type_name')

        shift_type_choices = [("", "همه")]
        shift_type_choices += [(str(st.id_shift_type), st.shift_type_name) for st in shift_types]

        self.fields['shift_type'] = forms.ChoiceField(
            choices=shift_type_choices,
            label='نوع شیفت',
            initial=selected_shift_type_id,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_shift_type',

            })
        )

        # --- ۴. شماره شیفت (وابسته به نوع شیفت) ---
        shift_name_choices = [("", "همه")]

        if selected_shift_type_id:
            # گرفتن شماره شیفت‌های مربوط به این نوع شیفت
            names = Shift.objects.filter(
                id_shift_type=selected_shift_type_id,
                active=True,
                del_field=False
            ).values_list('shift_name', flat=True).distinct().order_by('shift_number')

            if names:
                shift_name_choices += [(str(n), str(n)) for n in names]

        self.fields['shift_name'] = forms.ChoiceField(
            choices=shift_name_choices,
            label='شماره شیفت',
            initial=selected_shift_name,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_shift_name',
                'disabled': not bool(selected_shift_type_id)
            })
        )




# from django import forms
# # from sqlalchemy import between
#
# from sound_recorders.models import Shift_Type,Shift
# from information.employment_info.models import CurrentJob,JobLevels,Levels
# from .models import ShiftRate, Shift_Types
#
#
# class JobForm(forms.Form):
#     current_job = forms.ChoiceField(label='شغل فعلی',choices=[],widget=forms.Select(attrs={'class':'form-control','id':'current-job-select','data-url': '/api/Levels'}))
#     job_level = forms.ChoiceField(label='رده شغلی',choices=[('','ابتدا شغل فعلی را انتخاب کنید ')],required=False,widget=forms.Select(attrs={'class':'form-control','id':'job-level-select','disabled': 'disabled'}))
#     shift_type = forms.ChoiceField(label='نوع شیفت',choices=[],widget=forms.Select(attrs={'class':'form-control','id':'shift-type-select','data-url': '/api/shift-number'}))
#     shift_name = forms.ChoiceField(label='شماره شیفت',required=False)
#     # shift_rate = forms.DecimalField(label='نرخ شیفت',max_digits=18,decimal_places=0,required=False)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         shift_type = [(str(sh.id_shift_type), sh.shift_type_name) for sh in Shift_Types.objects.filter(active=True,del_field=False)]
#         self.fields["shift_type"].choices = [
#             ("", "انتخاب کنید"),
#         ] + shift_type
#
#         levels = [(str(l.id_levels), l.levels) for l in JobLevels.objects.filter(active=True,del_field=False)]
#         self.fields["levels"].choices = [
#             ("", "انتخاب کنید"),
#         ] + levels
#
#         # levels = [(str(l.id_levels), l.levels) for l in Levels.objects.filter(id_levels__in=JobLevels.objects.filter(active=True,del_field=False)) ]
#         # self.fields["levels"].choices = [
#         #     ("", "انتخاب کنید"),
#         # ] + levels
#
#         current_job = [(str(c.id_current_job), c.current_job) for c in CurrentJob.objects.filter(active=True,del_field=False,is_seda=True)]
#         self.fields["current_job"].choices = [
#             ("", "انتخاب کنید"),
#         ] + current_job
#
#         # current_job = [(str(c.id_current_job), c.current_job) for c in CurrentJob.objects.filter(JobLevels__current_job_id=15)]
#         # self.fields["current_job"].choices = [
#         #     ("", "انتخاب کنید"),
#         # ] + current_job
#
#         shift_name = [(str(sh.id_shift), sh.shift_name) for sh in Shift.objects.filter(active=True,del_field=False)]
#         self.fields["shift_name"].choices = [
#             ("", "انتخاب کنید"),
#         ] + shift_name
# from django import forms
# from django.core.exceptions import ValidationError
# from .models import VShiftLevelJob, ShiftRate
#
#
# class FilterForm(forms.Form):
#     """فرم فیلتر برای جدول"""
#     current_job = forms.ChoiceField(
#         label="شغل فعلی",
#         required=False,
#         choices=[('', '--- همه شغل‌ها ---')],
#         widget=forms.Select(attrs={
#             'class': 'form-control filter-select',
#             'style': 'width: 180px; height: 35px; font-size: 12px;',
#             'id': 'filter-current-job'
#         })
#     )
#
#     levels = forms.ChoiceField(
#         label="رده شغلی",
#         required=False,
#         choices=[('', '--- همه رده‌ها ---')],
#         widget=forms.Select(attrs={
#             'class': 'form-control filter-select',
#             'style': 'width: 180px; height: 35px; font-size: 12px;',
#             'id': 'filter-levels',
#             'disabled': True
#         })
#     )
#
#     shift_type = forms.ChoiceField(
#         label="نوع شیفت",
#         required=False,
#         choices=[('', '--- همه انواع ---')],
#         widget=forms.Select(attrs={
#             'class': 'form-control filter-select',
#             'style': 'width: 180px; height: 35px; font-size: 12px;',
#             'id': 'filter-shift-type'
#         })
#     )
#
#     shift_name = forms.ChoiceField(
#         label="شماره شیفت",
#         required=False,
#         choices=[('', '--- همه شماره‌ها ---')],
#         widget=forms.Select(attrs={
#             'class': 'form-control filter-select',
#             'style': 'width: 180px; height: 35px; font-size: 12px;',
#             'id': 'filter-shift-number',
#             'disabled': True
#         })
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # پر کردن dropdownها از ویو
#         self._populate_choices()
#
#         # اگر مقادیری از قبل انتخاب شده بودند (از GET)
#         self._restore_selections()
#
#     def _populate_choices(self):
#         """پر کردن dropdownها از ویو"""
#         # شغل‌ها (فقط فعال و سدا)
#         jobs = VShiftLevelJob.objects.values(
#             'id_current_job', 'current_job'
#         ).distinct().order_by('current_job')
#
#         self.fields['current_job'].choices += [
#             (str(job['id_current_job']), job['current_job'])
#             for job in jobs
#         ]
#
#         # نوع شیفت‌ها
#         shift_types = VShiftLevelJob.objects.values(
#             'id_shift_type', 'shift_type_name'
#         ).distinct().order_by('shift_type_name')
#
#         self.fields['shift_type'].choices += [
#             (str(st['id_shift_type']), st['shift_type_name'])
#             for st in shift_types
#         ]
#
#     def _restore_selections(self):
#         """بازیابی انتخاب‌های قبلی"""
#         current_job = self.data.get('current_job') if self.data else None
#         shift_type = self.data.get('shift_type') if self.data else None
#
#         if current_job and current_job != '':
#             # فعال کردن و پر کردن رده‌ها
#             self.fields['levels'].widget.attrs.pop('disabled', None)
#             levels = self._get_levels_for_job(current_job)
#             self.fields['levels'].choices = [('', '--- همه رده‌ها ---')] + levels
#
#         if shift_type and shift_type != '':
#             # فعال کردن و پر کردن شماره شیفت‌ها
#             self.fields['shift_name'].widget.attrs.pop('disabled', None)
#             shift_numbers = self._get_shift_numbers_for_type(shift_type)
#             self.fields['shift_name'].choices = [('', '--- همه شماره‌ها ---')] + shift_numbers
#
#     def _get_levels_for_job(self, job_id):
#         """دریافت رده‌های مربوط به یک شغل"""
#         try:
#             levels = VShiftLevelJob.objects.filter(
#                 id_current_job=int(job_id)
#             ).values('id_levels', 'levels').distinct().order_by('level_order')
#
#             return [
#                 (str(level['id_levels']), level['levels'])
#                 for level in levels
#             ]
#         except (ValueError, TypeError):
#             return []
#
#     def _get_shift_numbers_for_type(self, shift_type_id):
#         """دریافت شماره شیفت‌های مربوط به یک نوع شیفت"""
#         try:
#             shifts = VShiftLevelJob.objects.filter(
#                 id_shift_type=int(shift_type_id)
#             ).values('shift_name').distinct().order_by('shift_name')
#
#             return [
#                 (str(shift['shift_name']), f"شیفت {shift['shift_name']}")
#                 for shift in shifts
#             ]
#         except (ValueError, TypeError):
#             return []
#
#
# class BulkShiftRateForm(forms.Form):
#     """فرم دسته‌ای برای ویرایش نرخ‌ها"""
#
#     def __init__(self, *args, shift_rates=None, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         if shift_rates:
#             for shift_rate in shift_rates:
#                 field_name = f'shift_rate_{shift_rate.id_shift_rate}'
#                 self.fields[field_name] = forms.DecimalField(
#                     initial=shift_rate.shift_rate,
#                     required=True,
#                     max_digits=18,
#                     decimal_places=0,
#                     widget=forms.NumberInput(attrs={
#                         'class': 'form-control shift-rate-input editable',
#                         'style': 'width: 120px; text-align: left; direction: ltr;',
#                         'data-id': shift_rate.id_shift_rate,
#                         'step': '1000',
#                         'min': '0'
#                     })
#                 )
# setting/shift_rate/forms.py
# setting/shift_rate/forms.py
# forms.py
from django import forms
# from information.employment_info.models import CurrentJob, JobLevels
# from sound_recorders.models import Shift_Type, Shift
#
#
# class ShiftRateFilterForm(forms.Form):
#     job = forms.ChoiceField(
#         label='شغل',
#         choices=[('', 'همه')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'job_select'})
#     )
#
#     level = forms.ChoiceField(
#         label='رده',
#         choices=[('', 'همه')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'level_select', 'disabled': True})
#     )
#
#     shift_type = forms.ChoiceField(
#         label='نوع شیفت',
#         choices=[('', 'همه')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'shift_type_select'})
#     )
#
#     shift_name = forms.ChoiceField(
#         label='شماره شیفت',
#         choices=[('', 'همه')],
#         required=False,
#         widget=forms.Select(attrs={'class': 'form-select', 'id': 'shift_number_select', 'disabled': True})
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # پر کردن شغل‌ها
#         jobs = CurrentJob.objects.filter(active=True, del_field=False, is_seda=True)
#         self.fields['job'].choices += [(str(j.id_current_job), j.current_job) for j in jobs]
#
#         # پر کردن نوع شیفت
#         shift_types = Shift_Type.objects.filter(active=True, del_field=False)
#         self.fields['shift_type'].choices += [(str(st.id_shift_type), st.shift_type_name) for st in shift_types]