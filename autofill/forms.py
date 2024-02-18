from django import forms
from django.core.exceptions import ValidationError
import re


class InitialForm(forms.Form):
    iin_or_bin = forms.CharField(label='Введите ИИН/БИН', max_length=12)


class AdditionalDataForm(forms.Form):
    IIK = forms.CharField(label='ИИК', max_length=20, required=False)
    BIK = forms.CharField(label='БИК', max_length=8, required=False)
    name_ip_or_too = forms.CharField(
        label='Наиманование ИП/ТОО (без аббревиатур "ИП/ТОО":)',
        max_length=100, required=False
    )
    bank = forms.CharField(
        label='Наименование вашего банка',
        max_length=50,
        required=False
    )
    phone = forms.CharField(label='Телефон', max_length=20, required=False)
    city = forms.CharField(
        label='Город, где расположена компания:',
        max_length=100,
        required=False
    )
    location = forms.CharField(
        label='Адрес ИП/ТОО',
        max_length=200,
        required=False
    )
    name_director = forms.CharField(
        label='Полное ФИО директора (в родительном падеже):',
        max_length=100,
        required=False
    )
    initials = forms.CharField(
        label='Фамилия и инициалы директора',
        max_length=100,
        required=False
    )

    ACTION_CHOICES = [
        ('charter', 'Устава'),
        ('founding_contract', 'Учредительного договора'),
        ('other', 'Другое'),
    ]

    action = forms.ChoiceField(
        label='На основании',
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect,
        initial='charter',
        required=False
    )
    other_action = forms.CharField(
        label='Введите, на основании чего действует контракт '
              '(в родительном падеже)',
        max_length=100, required=False
    )

    def clean_IIK(self):
        iik = self.cleaned_data['IIK']
        if not iik.startswith('KZ') or len(iik) != 20:
            raise ValidationError(
                'Первые две буквы должны быть KZ и общее кол-во знаков 20.'
            )
        return iik

    def clean_BIK(self):
        bik = self.cleaned_data['BIK']
        if len(bik) != 8 or not bik.isalnum():
            raise ValidationError(
                'БИК должен состоять из 8 буквенно-цифровых символов.'
            )
        return bik

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r"^\+?1?\d{8,15}$", phone):
            raise ValidationError('Неверный формат номера телефона.')
        return phone