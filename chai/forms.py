from django import forms
from .models import ChaiVariety

class ChaiVarietyForm(forms.Form):
    chai_variety = forms.ModelChoiceField(
        queryset=ChaiVariety.objects.all(),
        label="Select Chai Variety",
        widget=forms.Select(attrs={
            'class': 'text-black bg-[#eff6ff] border border-gray-300 rounded-md p-1'
        })
    )
