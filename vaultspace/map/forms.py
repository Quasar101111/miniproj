from django import forms
from .models import Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude', 'description']
        widgets = {
            'latitude': forms.TextInput(attrs={'readonly': 'readonly', 'id': 'latitude'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly', 'id': 'longitude'}),
        }
