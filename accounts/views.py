# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from .forms import CustomUserCreationForm, TaxNumberRegistrationForm
from .models import UserProfile, InvitationToken
from companies.models import CompanyProfile
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import datetime

User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Felhasználó legyen aktív az alapregisztráció után
            user.save()

            # UserProfile létrehozása (profil kitöltése még hátravan)
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': UserProfile.ROLE_ESG_FELELOS,
                    'profile_setup_complete': False
                }
            )
            if not created:
                user_profile.role = UserProfile.ROLE_ESG_FELELOS
                user_profile.profile_setup_complete = False
                user_profile.save()

            # InvitationToken generálása a profil kitöltéséhez
            profile_token = InvitationToken.objects.create(
                email=user.email,
            )

            # URL generálása a profil kitöltő oldalhoz
            complete_profile_url_path = reverse('accounts:register_with_token', kwargs={'token_uuid': profile_token.token})
            complete_profile_full_url = request.build_absolute_uri(complete_profile_url_path)

            # E-mail küldése a felhasználónak
            try:
                subject = 'Sikeres regisztráció - ESG AutoReport Profil Véglegesítése'
                message_body = (
                    f"Kedves {user.first_name or user.username},\n\n"
                    f"Köszönjük regisztrációdat az ESG AutoReport rendszerbe!\n\n"
                    f"Fiókod sikeresen létrejött. A következő lépés a vállalati profilod és adataid megadása.\n"
                    f"Kérjük, kattints az alábbi linkre a folyamat befejezéséhez:\n"
                    f"{complete_profile_full_url}\n\n"
                    f"Ha a link nem kattintható, másold be a böngésződ címsorába.\n"
                    f"A link érvényessége: 7 nap.\n\n"
                    f"Üdvözlettel,\nAz ESG AutoReport Csapata"
                )
                send_mail(
                    subject, message_body, settings.DEFAULT_FROM_EMAIL,
                    [user.email], fail_silently=False
                )
            except Exception as e:
                messages.error(request, _("Hiba történt az értesítő e-mail küldése közben. Kérjük, próbáld meg később a profilod kitöltését, vagy lépj kapcsolatba az ügyfélszolgálattal."))

            # Átirányítás az "utasításokat tartalmazó" oldalra
            return redirect(reverse('accounts:registration_show_token_link') + f'?token={profile_token.token}&url={complete_profile_full_url}')

    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Regisztráció'
    }
    return render(request, 'accounts/signup.html', context)

def registration_show_token_link_view(request):
    token = request.GET.get('token')
    url = request.GET.get('url')
    context = {
        'page_title': 'Regisztráció Sikeres - Következő Lépés',
        'profile_setup_token': token,
        'complete_profile_url': url,
        'user_email': request.user.email if request.user.is_authenticated else None
    }
    return render(request, 'accounts/registration_show_token_link.html', context)

def registration_pending_view(request):
    context = {
        'page_title': 'Regisztráció Fogadva'
    }
    return render(request, 'accounts/registration_pending.html', context)

def register_with_token_view(request, token_uuid):
    try:
        invitation_token = get_object_or_404(InvitationToken, token=token_uuid)
    except ValueError:
        messages.error(request, _("Érvénytelen meghívó formátum."))
        return redirect('dashboard:home')

    if not invitation_token.is_valid():
        messages.error(request, _("Ez a regisztrációs meghívó már nem érvényes. Kérj újat az adminisztrátortól."))
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = TaxNumberRegistrationForm(request.POST, initial={'token': token_uuid})
        if form.is_valid():
            # Felhasználói adatok a formból
            user_email = form.cleaned_data['user_email']
            user_first_name = form.cleaned_data['user_first_name']
            user_last_name = form.cleaned_data['user_last_name']
            password = form.cleaned_data['password']

            # Cégadatok a formból
            company_name = form.cleaned_data['company_name']
            tax_number = form.cleaned_data['tax_number']
            registration_number = form.cleaned_data.get('registration_number')
            address_country = form.cleaned_data.get('address_country')
            address_postal_code = form.cleaned_data.get('address_postal_code')
            address_city = form.cleaned_data.get('address_city')
            address_street_and_number = form.cleaned_data.get('address_street_and_number')
            questionnaire_type_key = form.cleaned_data['questionnaire_type']

            if User.objects.filter(email=user_email).exists():
                form.add_error('user_email', _("Ez az e-mail cím már regisztrálva van a rendszerben."))

            username_candidate = user_email.split('@')[0]
            temp_username = username_candidate
            counter = 1
            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{username_candidate}_{counter}"
                counter += 1

            if not form.errors:
                # A tokenhez tartozó felhasználó UserProfile-jának lekérése
                try:
                    registered_user = User.objects.get(email=invitation_token.email)
                    user_profile_to_update = registered_user.profile
                except User.DoesNotExist:
                    messages.error(request, _("Hiba: A regisztrációhoz tartozó felhasználó nem található."))
                    return redirect('accounts:signup')
                except UserProfile.DoesNotExist:
                    messages.error(request, _("Hiba: A felhasználói profil nem található."))
                    return redirect('accounts:signup')

                # CompanyProfile létrehozása vagy frissítése
                company_profile, created_company = CompanyProfile.objects.update_or_create(
                    tax_number=tax_number,
                    defaults={
                        'name': company_name,
                        'registration_number': registration_number,
                        'address_country': address_country,
                        'address_postal_code': address_postal_code,
                        'address_city': address_city,
                        'address_street_and_number': address_street_and_number,
                        # 'industry' (TEÁOR) mező hozzáadása később, ha szükséges
                    }
                )

                # UserProfile frissítése
                user_profile_to_update.company = company_profile
                user_profile_to_update.primary_questionnaire_type = questionnaire_type_key  # A formból
                user_profile_to_update.profile_setup_complete = True
                user_profile_to_update.save()

                invitation_token.status = InvitationToken.STATUS_USED
                invitation_token.save()

                # Felhasználó bejelentkeztetése
                login(request, user_profile_to_update.user)
                messages.success(request, _("Profil sikeresen frissítve! Üdvözlünk a rendszerben."))
                return redirect('dashboard:home')
    else:
        initial_data = {'token': token_uuid}
        if invitation_token.email:
            initial_data['user_email'] = invitation_token.email
        form = TaxNumberRegistrationForm(initial=initial_data)

    context = {
        'form': form,
        'token_object': invitation_token,
        'page_title': _('Regisztráció Meghívóval')
    }
    return render(request, 'accounts/register_with_token.html', context)