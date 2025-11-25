from django import forms
from .models import FormulaSetting

class SalaryForm(forms.ModelForm):
    class Meta:
        model = FormulaSetting
        fields = ['hire_status', 'formula']
        widgets = {
            'hire_status': forms.TextInput(attrs={'placeholder': ''}),
            'formula': forms.TextInput(attrs={'placeholder': ''}),
        }
