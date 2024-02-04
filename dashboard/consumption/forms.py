# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('id', 'area', 'tariff')
