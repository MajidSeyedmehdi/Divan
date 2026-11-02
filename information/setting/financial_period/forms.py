from jalali_date.widgets import AdminJalaliDateWidget
from django_jalali.forms import jDateField
from django import forms
import jdatetime

from django import forms




class FinancialPeriodForm(forms.Form):
    start_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ شروع",
        required=False
    )
    end_date = jDateField(
        widget=AdminJalaliDateWidget(attrs={'class': 'form-control'}),
        label="تاریخ پایان",
        required=False
    )
    description = forms.CharField(
        label='توضیحات',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'توضیحات دوره مالی'
        }),
        required=False
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     # محاسبه تاریخ‌های پیش‌فرض (یک ماه قبل از امروز)
    #     today = jdatetime.date.today()
    #     one_month_ago = today - jdatetime.timedelta(days=30)
    #
    #     # تنظیم تاریخ شروع به یک ماه قبل
    #     if not self.initial.get('start_date'):
    #         self.initial['start_date'] = one_month_ago
    #
    #     # تنظیم تاریخ پایان به امروز
    #     if not self.initial.get('end_date'):
    #         self.initial['end_date'] = today
    #
    #     # تنظیم توضیحات پیش‌فرض
    #     if not self.initial.get('description'):
    #         self.initial['description'] = f"دوره مالی ({today.year}/{today.month})"