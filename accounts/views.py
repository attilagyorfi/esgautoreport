# accounts/views.py
from django.shortcuts import render, redirect
# Az 'login' importra már nem lesz szükségünk itt, mert nem jelentkezettjük be automatikusan
# from django.contrib.auth import login 
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.core.mail import send_mail # E-mail küldéshez
from django.conf import settings # A settings.py beállítások eléréséhez
from django.template.loader import render_to_string # E-mail sablonhoz

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Még ne mentsük az adatbázisba
            user.is_active = False  # <<< ÚJ: A felhasználó inaktív lesz regisztrációkor
            user.save() # Most mentjük a User objektumot

            # UserProfile létrehozása az új felhasználóhoz
            UserProfile.objects.create(
                user=user,
                role=UserProfile.ROLE_ESG_FELELOS, # Vagy egy 'pending_approval' szerepkör, ha lenne
                company=None 
            )
            
            # Adminisztrátori értesítő e-mail küldése
            try:
                subject = 'Új felhasználói regisztráció az ESG AutoReport rendszerben'
                # Készíthetünk egy egyszerű szöveges e-mailt, vagy egy HTML sablont is
                message_context = {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    # Ide tehetsz egy linket az admin felületre a felhasználó szerkesztéséhez
                    'admin_user_url': request.build_absolute_uri(f'/admin/auth/user/{user.pk}/change/')
                }
                # Egyszerű szöveges üzenet:
                # message = f"Új felhasználó regisztrált:\nNév: {user.username}\nEmail: {user.email}\nKeresztnév: {user.first_name}\nVezetéknév: {user.last_name}\n\nJóváhagyáshoz kattints ide: {message_context['admin_user_url']}"
                
                # Használhatunk egy egyszerűbb szöveges e-mailt, vagy egy HTML sablont is
                # Most egy egyszerű szövegeset:
                message_body = (
                    f"Kedves Admin,\n\n"
                    f"Egy új felhasználó regisztrált az ESG AutoReport rendszerbe, jóváhagyásra vár.\n\n"
                    f"Felhasználónév: {user.username}\n"
                    f"E-mail cím: {user.email}\n"
                    f"Vezetéknév: {user.last_name}\n"
                    f"Keresztnév: {user.first_name}\n\n"
                    f"A felhasználó aktiválásához és szerkesztéséhez kattints az alábbi linkre (vagy másold be a böngésződbe):\n"
                    f"{message_context['admin_user_url']}\n\n"
                    f"Üdvözlettel,\nAz ESG AutoReport Rendszer"
                )

                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL, # A feladó e-mail címe (settings.py-ből)
                    ['info@g2amarketing.hu'],    # A címzett(ek) listája
                    fail_silently=False, # Ha True, nem dob hibát, ha az e-mail küldés nem sikerül
                )
            except Exception as e:
                # Itt naplózhatnánk a hibát, ha az e-mail küldés nem sikerül
                print(f"Hiba az admin értesítő e-mail küldésekor: {e}")

            # <<< ÚJ: Átirányítás egy "regisztráció fogadva, jóváhagyásra vár" oldalra
            return redirect('accounts:registration_pending') 
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'page_title': 'Regisztráció'
    }
    return render(request, 'accounts/signup.html', context)

def registration_pending_view(request):
    context = {
        'page_title': 'Regisztráció Fogadva'
    }
    return render(request, 'accounts/registration_pending.html', context)