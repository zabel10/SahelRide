from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Voiture, Reservation, Paiement, Avis

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['email','nom','prenom','type_utilisateur','is_staff']
    list_filter = ['type_utilisateur','is_staff']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email','password')}),
        ('Infos personnelles', {'fields': ('nom','prenom','telephone','type_utilisateur')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email','nom','prenom','password1','password2','type_utilisateur')}),
    )
    search_fields = ['email','nom','prenom']

@admin.register(Voiture)
class VoitureAdmin(admin.ModelAdmin):
    list_display = ['marque','modele','ville','disponibilite','prix_jour','nb_locations']
    list_filter = ['ville','disponibilite','marque']
    search_fields = ['marque','modele','immatriculation']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id','utilisateur','voiture','date_debut','date_fin','prix_total','statut_reservation']
    list_filter = ['statut_reservation']

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['id','reservation','montant','mode_paiement','etat_paiement']

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ['utilisateur','voiture','note','date_avis']
