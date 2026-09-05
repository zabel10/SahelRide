from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('voitures/', views.toutes_voitures, name='toutes_voitures'),
    path('voitures/<int:pk>/', views.detail_voiture, name='detail_voiture'),
    path('par-ville/', views.par_ville, name='par_ville'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('reserver/<int:pk>/', views.reserver, name='reserver'),
    path('paiement/<int:pk>/', views.paiement, name='paiement'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Admin – gestion propriétaires
    path('dashboard/proprietaires/', views.admin_creer_proprietaire, name='admin_creer_proprietaire'),
    path('dashboard/proprietaires/<int:pk>/supprimer/', views.admin_supprimer_proprietaire, name='admin_supprimer_proprietaire'),
    # Espace propriétaire
    path('espace-proprio/', views.proprio_dashboard, name='proprio_dashboard'),
    path('espace-proprio/ajouter/', views.proprio_ajouter_voiture, name='proprio_ajouter_voiture'),
    path('espace-proprio/modifier/<int:pk>/', views.proprio_modifier_voiture, name='proprio_modifier_voiture'),
    path('espace-proprio/supprimer/<int:pk>/', views.proprio_supprimer_voiture, name='proprio_supprimer_voiture'),
    path('espace-proprio/reservation/<int:pk>/statut/', views.proprio_changer_statut_resa, name='proprio_changer_statut_resa'),
]
