# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .models import UserProfile, InvitationToken
from companies.models import CompanyProfile
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .choices import QUESTIONNAIRE_TYPE_CHOICES

def register_with_token_view(request, token_uuid):
    try:
        invitation_token = get_object_or_404(InvitationToken, token=token_uuid)
    except ValueError:
        messages.error(request, _("Érvénytelen meghívó formátum."))
        return redirect('dashboard:home')

    if not invitation_token.is_valid():
        messages.error(request, _("Ez a regisztrációs meghívó már nem érvényes (lejárt vagy felhasználták). Kérj újat az adminisztrátortól."))
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = TaxNumberRegistrationForm(request.POST, initial={'token': token_uuid})
        if form.is_valid():
            tax_number = form.cleaned_data['tax_number']
            user_email = form.cleaned_data['user_email']
            user_first_name = form.cleaned_data['user_first_name']
            user_last_name = form.cleaned_data['user_last_name']
            password = form.cleaned_data['password']

            if User.objects.filter(email=user_email).exists():
                form.add_error('user_email', _("Ez az e-mail cím már regisztrálva van a rendszerben."))

            username_candidate = user_email.split('@')[0]
            temp_username = username_candidate
            counter = 1
            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{username_candidate}_{counter}"
                counter += 1

            if not form.errors:
                company_data_from_api = fetch_company_data_by_tax_number(tax_number)
                if not company_data_from_api or not company_data_from_api.get('name'):
                    form.add_error('tax_number', _("Nem sikerült adatokat lekérdezni ehhez az adószámhoz, vagy a válasz hiányos volt."))
                else:
                    company_profile, created_company = CompanyProfile.objects.update_or_create(
                        tax_number=tax_number,
                        defaults={
                            'name': company_data_from_api.get('name', 'N/A'),
                            'address_country': company_data_from_api.get('address_country', 'Magyarország'),
                            'address_postal_code': company_data_from_api.get('address_postal_code', ''),
                            'address_city': company_data_from_api.get('address_city', ''),
                            'address_street_and_number': company_data_from_api.get('address_street_and_number', ''),
                            'registration_number': company_data_from_api.get('registration_number', ''),
                        }
                    )

                    new_user = User.objects.create_user(
                        username=temp_username,
                        email=user_email,
                        password=password,
                        first_name=user_first_name,
                        last_name=user_last_name,
                        is_active=True
                    )

                    questionnaire_type_key = determine_questionnaire_type(company_data_from_api)

                    UserProfile.objects.create(
                        user=new_user,
                        company=company_profile,
                        role=UserProfile.ROLE_ESG_FELELOS,
                        primary_questionnaire_type=questionnaire_type_key,
                        profile_setup_complete=True
                    )

                    invitation_token.status = InvitationToken.STATUS_USED
                    invitation_token.save()

                    login(request, new_user)
                    messages.success(request, _("Sikeres regisztráció! Üdvözlünk a rendszerben."))
                    return redirect('dashboard:home')
    else:
        initial_data = {'token': token_uuid}
        if invitation_token.email:
            initial_data['user_email'] = invitation_token.email
        form = TaxNumberRegistrationForm(initial=initial_data)

    context = {
        'form': form,
        'token_object': invitation_token,
        'page_title': _('Regisztráció Adószámmal')
    }
    return render(request, 'accounts/register_with_token.html', context)

def fetch_company_data_by_tax_number(tax_number):
    # Itt lehetne külső API hívás
    if tax_number == "11111111-1-11":
        return {
            'name': "Minta Teszt Vállalat Kft.",
            'address_country': "Magyarország",
            'address_postal_code': "1111",
            'address_city': "Budapest",
            'address_street_and_number': "Teszt utca 1.",
            'registration_number': "01-09-111111",
            'company_size_indicator': 'kozepvall',
        }
    return None

def determine_questionnaire_type(company_api_data):
    size_indicator = company_api_data.get('company_size_indicator')
    if size_indicator == 'nagyvall':
        return 'sztfh_nagyvall_hu_egt_ch'
    elif size_indicator == 'kozepvall':
        return 'sztfh_kozepvall_hu_egt_ch'
    elif size_indicator == 'kisvall':
        return 'sztfh_kisvall_hu_egt_ch'
    elif size_indicator == 'mikrovall':
        return 'sztfh_mikrovall_hu_egt_ch'
    return 'sztfh_sajat_teljes'

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("E-mail cím"),
        required=True,
        help_text=_("Kötelező. Érvényes e-mail cím.")
    )
    first_name = forms.CharField(
        label=_("Keresztnév"),
        max_length=30,
        required=False,
        help_text=_("Opcionális.")
    )
    last_name = forms.CharField(
        label=_("Vezetéknév"),
        max_length=150,
        required=False,
        help_text=_("Opcionális.")
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

        labels = {
            'username': _('Felhasználónév'),
            'password2': _('Jelszó megerősítése'),
        }
        help_texts = {
            'username': _("Kötelező. Max. 150 karakter. Csak betűk, számok és @/./+/-/_ karakterek."),
        }

class TaxNumberRegistrationForm(forms.Form):
    # Felhasználói adatok
    user_email = forms.EmailField(
        label=_("Az Ön E-mail Címe"),
        required=True,
        help_text=_("Erre az e-mail címre küldjük a további információkat.")
    )
    user_first_name = forms.CharField(
        label=_("Keresztnév"),
        max_length=30,
        required=True
    )
    user_last_name = forms.CharField(
        label=_("Vezetéknév"),
        max_length=150,
        required=True
    )
    password = forms.CharField(label=_("Jelszó"), widget=forms.PasswordInput)
    password_confirm = forms.CharField(label=_("Jelszó megerősítése"), widget=forms.PasswordInput)

    # Cégadatok
    company_name = forms.CharField(
        label=_("Vállalat Hivatalos Neve"),
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Pl. Minta Kft.'})
    )
    tax_number = forms.CharField(
        label=_("Vállalat Adószáma"),
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Pl. 12345678-1-23'}),
        help_text=_("Kérjük, adja meg a vállalat adószámát.")
    )
    registration_number = forms.CharField(
        label=_("Cégjegyzékszám (opcionális)"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Pl. 01-09-123456'})
    )
    address_country = forms.CharField(
        label=_("Ország"),
        max_length=100,
        required=False,
        initial="Magyarország"
    )
    address_postal_code = forms.CharField(
        label=_("Irányítószám"),
        max_length=20,
        required=False
    )
    address_city = forms.CharField(
        label=_("Város"),
        max_length=100,
        required=False
    )
    address_street_and_number = forms.CharField(
        label=_("Utca, házszám"),
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'rows': 2})
    )

    questionnaire_type = forms.ChoiceField(
        label=_("Kitöltendő Kérdőív Típusa"),
        choices=QUESTIONNAIRE_TYPE_CHOICES,  # Itt használod az importált listát
        required=True,
        widget=forms.Select()
    )

    token = forms.CharField(widget=forms.HiddenInput())

    def clean_tax_number(self):
        tax_number = self.cleaned_data.get('tax_number')
        return tax_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', _("A két jelszó nem egyezik."))
        return cleaned_data