from django import forms
from django.core.exceptions import ValidationError
import re
from autofill.meta.bank_list import BANK_CHOICES


class InitialForm(forms.Form):
    iin_or_bin = forms.CharField(label='Введите ИИН/БИН', max_length=12)

    def clean_iin_or_bin(self):
        iin_or_bin = self.cleaned_data['iin_or_bin']
        if not re.fullmatch(r'\d{12}', iin_or_bin):
            raise ValidationError('ИИН/БИН должен состоять из 12 цифр.')
        return iin_or_bin


class AdditionalDataForm(forms.Form):
    IIK = forms.CharField(
        label='ИИК (номер лицевого счета) в вашем Банке',
        max_length=20,
        required=False,
        initial='KZ'
    )
    BIK = forms.CharField(
        label='БИК вашего Банка',
        max_length=8,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'пример: CASPKZKA'})
    )
    name_ip_or_too = forms.CharField(
        label='Наиманование ИП/ТОО без кавычек и без аббревиатур ИП/ТОО',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'пример: Береке'})
    )
    bank = forms.ChoiceField(
        label='Наименование вашего Банка (выберите из выпадающего списка)',
        choices=BANK_CHOICES,
        required=False
    )
    other_bank = forms.CharField(
        label='Укажите наименование вашего Банка',
        max_length=100,
        required=False,
        initial='АО «»',
        widget=forms.TextInput(attrs={
            'style': 'display:none;',
            'placeholder': 'пример: АО «Народный Банк Казахстана»'})
    )
    phone = forms.CharField(
        label='Телефон (в формате +7 XXX XXX XX XX)',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'пример: + 7 701 777 77 77'})
    )
    city = forms.CharField(
        label='Город, где расположена компания(без обозначения "г./город", только название):',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'пример: Алматы'})
    )
    location = forms.CharField(
        label='Адрес ИП/ТОО',
        max_length=200,
        required=False,
        widget=forms.Textarea(
            attrs={'placeholder': 'пример: Республика Казахстан, 050051, '
                                  'г. Алматы, Медеуский Район, мкр. Самал-2, д. 1',
                   'rows': 2,
                   'style': 'resize:none;'
                   },
        )
    )
    name_director = forms.CharField(
        label='Полное ФИО директора (в родительном падеже):',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'пример: Ахметова Армана Бериковича'})
    )
    initials = forms.CharField(
        label='Фамилия и инициалы директора',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'пример: Ахметов А.Б.'})
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
