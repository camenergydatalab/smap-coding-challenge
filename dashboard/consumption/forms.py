# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Consumption, User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('id', 'area', 'tariff')


class ConsumptionForm(forms.ModelForm):

    class Meta:
        model = Consumption
        fields = ('user', 'datetime', 'value')
