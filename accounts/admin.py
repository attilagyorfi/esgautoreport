# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile # Importáljuk a UserProfile modellt

# Először "unregister"eljük az alap UserAdmin-t, hogy aztán sajátot adhassunk hozzá
# admin.site.unregister(User) # Erre csak akkor van szükség, ha a UserAdmin-t teljesen felülírnánk, most nem ez a cél.

# Definiálunk egy inline admin-t a UserProfile-hoz, hogy a User szerkesztő oldalán jelenjen meg
class UserProfileInline(admin.StackedInline): # Vagy admin.TabularInline a táblázatosabb megjelenésért
    model = UserProfile
    can_delete = False # Általában nem akarjuk, hogy a User törlésével együtt törlődjön a profil, vagy fordítva innen.
    verbose_name_plural = 'Felhasználói Profil'
    fk_name = 'user'

# Definiáljuk az új UserAdmin-t, ami tartalmazza a UserProfileInline-t
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_profile_company', 'get_user_profile_role')
    list_select_related = ('profile',) # Optimalizálja a lekérdezést a profil adatokhoz

    def get_user_profile_company(self, instance):
        if hasattr(instance, 'profile') and instance.profile.company:
            return instance.profile.company.name
        return None
    get_user_profile_company.short_description = 'Vállalat (Profilból)'

    def get_user_profile_role(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.get_role_display()
        return None
    get_user_profile_role.short_description = 'Szerepkör (Profilból)'


# Regisztráljuk újra a User modellt a mi CustomUserAdmin-unkkal
admin.site.unregister(User) # Először töröljük a régit
admin.site.register(User, CustomUserAdmin) # Majd regisztráljuk az újat

# Külön is regisztrálhatjuk a UserProfile-t, ha külön listában is szeretnénk kezelni őket
# De az inline megjelenítés a User oldalon általában praktikusabb.
# Ha mégis szeretnéd külön is:
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'company', 'role', 'created_at')
#     list_select_related = ('user', 'company') # Optimalizálás
#     search_fields = ('user__username', 'company__name', 'role')
#     list_filter = ('role', 'company')