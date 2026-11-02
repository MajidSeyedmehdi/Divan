from django import forms

from sound_recorders.models import Network


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='فایل Excel',
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control-file',
                'accept': '.xls,.xlsx'
            }
        )
    )

    class NetworkFilterForm(forms.Form):
        network = forms.ChoiceField(
            label="انتخاب شبکه",
            required=False,
            widget=forms.Select(attrs={'class': 'form-select'})
        )

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     # استخراج کلید اصلی و عنوان شبکه از دیتابیس
        #     networks = Network.objects.filter(
        #         Del=False,
        #         Active=True,
        #         Is_active=True
        #     ).values_list('Id_network', 'Network')
        #
        #     # افزودن گزینه "همه شبکه ها" در بالای لیست
        #     self.fields['network'].choices = [('all', 'همه شبکه ها')] + list(networks)

    network = forms.ModelChoiceField(
        queryset=Network.objects.filter(
            del_field=False,
            active=True,
            is_active=True
        ),
        label="انتخاب شبکه",
        empty_label="   انتخاب شبکه",
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )