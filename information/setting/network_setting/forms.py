from django import forms
from sound_recorders.current_affairs.sound_shift_search.models import SelectNetwork
from .models import Network_Setting

BOOLEAN_CHOICES = (
    ("", " "),   # 👈 خالی
    ("1", "دارد"),
    ("0", "ندارد"),
)

ACTIVE_CHOICES = (
    ("", ""),   # 👈 خالی
    ("1", "فعال"),
    ("0", "غیرفعال"),
)
class HeaderForm(forms.Form):

    network = forms.ModelChoiceField(queryset=SelectNetwork.objects.none(), label="شبکه", required=False, empty_label="انتخاب شبکه")
    shift_count = forms.ChoiceField(label="تعداد شیفت", required=False)
    coefficient = forms.ChoiceField(label="ضریب شیفت", required=False)
    has_live = forms.ChoiceField(label="وضعیت شبکه",
                                 choices=BOOLEAN_CHOICES,
                                 required=False)
    active = forms.ChoiceField(label="برنامه زنده",
                               choices=ACTIVE_CHOICES,
                               required=False)
    payable = forms.ChoiceField(label="مجوز پرداخت",
                               choices=BOOLEAN_CHOICES,
                               required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['network'].queryset = SelectNetwork.objects.all()

        shift_count = Network_Setting.objects.values_list('shift_count', 'shift_count').distinct()
        self.fields['shift_count'].choices = [('', '')] + list(shift_count)

        coefficient = Network_Setting.objects.values_list('coefficient', 'coefficient').distinct()
        self.fields['coefficient'].choices = [('', '')] + list(coefficient)

