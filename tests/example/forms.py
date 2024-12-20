# example/forms.py

from django import forms


class BestsellerMakerForm(forms.Form):
    keyword = forms.CharField()
