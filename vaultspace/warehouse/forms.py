# forms.py in warehouse_app
from django import forms
import datetime
from .models import Warehouse, WarehousePhoto

class WarehouseForm(forms.ModelForm):
    FACILITIES_CHOICES = [
        ('Loading Docks', 'Loading Docks'),
        ('Racking Systems', 'Racking Systems'),
        ('Lighting and Climate Control', 'Lighting and Climate Control'),
        ('Climate control', 'Climate control (including temperature and humidity management)'),
        ('Surveillance cameras', 'Surveillance cameras'),
        ('Access control systems', 'Access control systems (such as key cards or biometric access)'),
        ('Alarm systems', 'Alarm systems'),
        ('Security personnel', 'Security personnel'),
        ('Restrooms and break areas', 'Restrooms and break areas'),
        ('Office spaces', 'Office spaces for administrative tasks'),
        ('First aid stations', 'First aid stations'),
    ]

    facilities = forms.MultipleChoiceField(
        choices=FACILITIES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    current_year = datetime.date.today().year
    year_built = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1980, current_year + 1)),
        validators=[],
    )

    def clean_year_built(self):
        year_built = self.cleaned_data['year_built']
        if year_built > datetime.date.today():
            raise forms.ValidationError("The year cannot be in the future.")
        return year_built

    class Meta:
        model = Warehouse
        fields = [
            'location', 'area', 'ownership_documents','landmarks',
            'rental_price', 'terms_cond',
        ]

class WarehousePhotoForm(forms.ModelForm):
    class Meta:
        model = WarehousePhoto
        fields = ['image']