# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # Fordítható stringekhez (opcionális itt, de jó gyakorlat)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("E-mail cím"), # Label explicit beállítása itt
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
        # A jelszó mezőket a UserCreationForm örökíti, a fields listában nem kell őket külön kezelni,
        # ha csak az alap viselkedést akarjuk, de a labels és help_texts-ben hivatkozhatunk rájuk.
        fields = ("username", "email", "first_name", "last_name") 

        labels = {
            'username': _('Felhasználónév'),
            # Az email, first_name, last_name címkéket már a meződefiníciónál is beállíthattuk,
            # de itt is felülírhatók vagy központosíthatók.
            # 'email': _('E-mail cím'), # Példa, ha itt szeretnéd definiálni
            # 'first_name': _('Keresztnév'),
            # 'last_name': _('Vezetéknév'),
            'password2': _('Jelszó megerősítése'), # A UserCreationForm használja ezt a nevet a második jelszómezőhöz
        }
        help_texts = {
            'username': _("Kötelező. Max. 150 karakter. Csak betűk, számok és @/./+/-/_ karakterek."),
            # A jelszó mezők help text-jeit a UserCreationForm kezeli, és a LANGUAGE_CODE alapján lefordítja.
            # Ha egyéni súgószöveget szeretnél a jelszóhoz (password1), azt is megadhatod:
            # 'password1': _("A jelszónak legalább 8 karakter hosszúnak kell lennie... stb."),
        }
        # Hibaüzeneteket is testre szabhatnánk az error_messages szótárral, ha szükséges.