from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
import uuid

from .models import Voiture, Reservation, Paiement, Avis, Utilisateur, VILLES
from .forms import InscriptionForm, ConnexionForm, ReservationForm, PaiementForm, AvisForm, ContactForm


def is_admin(user):
    return user.is_authenticated and user.type_utilisateur == 'admin'


# -------- ACCUEIL ----------------------------------------------------
def accueil(request):
    voitures_populaires = Voiture.objects.filter(disponibilite='Disponible').order_by('-nb_locations')[:6]
    avis_recents = Avis.objects.select_related('utilisateur','voiture').all()[:6]
    avis_form = None
    if request.user.is_authenticated:
        avis_form = AvisForm()
    stats = {
        'nb_voitures': Voiture.objects.count(),
        'nb_clients': Utilisateur.objects.filter(type_utilisateur='client').count(),
        'nb_villes': 3,
    }
    return render(request, 'location/accueil.html', {
        'voitures': voitures_populaires,
        'avis_recents': avis_recents,
        'avis_form': avis_form,
        'stats': stats,
        'villes': VILLES,
    })


# ---- TOUTES LES VOITURES ----------------------------------------------------
def toutes_voitures(request):
    qs = Voiture.objects.all()
    ville = request.GET.get('ville', '')
    if ville:
        qs = qs.filter(ville=ville)
    return render(request, 'location/voitures.html', {'voitures': qs, 'ville_active': ville, 'villes': VILLES})


# ------- PAR VILLE --------------------------------------------------------------
def par_ville(request):
    ville = request.GET.get('ville', '')
    qs = Voiture.objects.filter(disponibilite='Disponible')
    if ville:
        qs = qs.filter(ville=ville)
    return render(request, 'location/par_ville.html', {'voitures': qs, 'ville_active': ville, 'villes': VILLES})


# ---- DETAIL VOITURE ----------------------------------------------------
def detail_voiture(request, pk):
    voiture = get_object_or_404(Voiture, pk=pk)
    avis_list = Avis.objects.filter(voiture=voiture).select_related('utilisateur')
    avis_form = AvisForm()
    resa_form = ReservationForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'submit_avis' in request.POST:
            avis_form = AvisForm(request.POST)
            if avis_form.is_valid():
                a = avis_form.save(commit=False)
                a.utilisateur = request.user
                a.voiture = voiture
                a.save()
                messages.success(request, 'Votre avis a été publié.')
                return redirect('detail_voiture', pk=pk)

    return render(request, 'location/detail_voiture.html', {
        'voiture': voiture,
        'avis_list': avis_list,
        'avis_form': avis_form,
        'resa_form': resa_form,
    })


# ---- INSCRIPTION -------------------------------------------------------
def inscription(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    next_url = request.GET.get('next', '')
    form = InscriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Bienvenue {user.prenom} ! Votre compte a été créé.')
        return redirect(next_url or 'accueil')
    return render(request, 'location/inscription.html', {'form': form, 'next': next_url})


# ---- CONNEXION -----------------------------------------------------------------
def connexion(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    next_url = request.GET.get('next', '')
    form = ConnexionForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Bienvenue {user.prenom} !')
        return redirect(next_url or 'accueil')
    return render(request, 'location/connexion.html', {'form': form, 'next': next_url})


# ---- DECONNEXION ----------------------------------------------------------------
def deconnexion(request):
    logout(request)
    return redirect('accueil')


# ---- RESERVATION ------------------------------------------------------------------
@login_required
def reserver(request, pk):
    voiture = get_object_or_404(Voiture, pk=pk, disponibilite='Disponible')
    resa_form = ReservationForm(request.POST or None)
    if request.method == 'POST' and resa_form.is_valid():
        resa = resa_form.save(commit=False)
        resa.utilisateur = request.user
        resa.voiture = voiture
        resa.save()
        # Mettre à jour compteur
        voiture.nb_locations += 1
        voiture.save()
        return redirect('paiement', pk=resa.pk)
    return render(request, 'location/reserver.html', {'voiture': voiture, 'form': resa_form})


# ---- PAIEMENT -----------------------------------------------------------------------
@login_required
def paiement(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, utilisateur=request.user)
    if hasattr(reservation, 'paiement'):
        return redirect('mes_reservations')
    form = PaiementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        p = form.save(commit=False)
        p.reservation = reservation
        p.montant = reservation.prix_total
        p.reference_transaction = str(uuid.uuid4())[:12].upper()
        p.etat_paiement = 'Validé'
        p.save()
        reservation.statut_reservation = 'Confirmée'
        reservation.save()
        messages.success(request, f'Paiement confirmé ! Référence : {p.reference_transaction}')
        return redirect('mes_reservations')
    return render(request, 'location/paiement.html', {'reservation': reservation, 'form': form})


# --- MES RESERVATIONS -------------------------------------------------------------
@login_required
def mes_reservations(request):
    reservations = Reservation.objects.filter(utilisateur=request.user).select_related('voiture').order_by('-date_reservation')
    return render(request, 'location/mes_reservations.html', {'reservations': reservations})


# ---- CONTACT ----------------------------------------------------------------------
def contact(request):
    form = ContactForm(request.POST or None)
    envoye = False
    if request.method == 'POST' and form.is_valid():
        envoye = True
        messages.success(request, 'Votre message a été envoyé. Nous vous répondrons sous 24h.')
    return render(request, 'location/contact.html', {'form': form, 'envoye': envoye})


# ----- DASHBOARD ADMIN ------------------------------------------------------------
@user_passes_test(is_admin, login_url='/connexion/')
def dashboard(request):
    voitures = Voiture.objects.all().order_by('-nb_locations')
    reservations = Reservation.objects.select_related('utilisateur','voiture').order_by('-date_reservation')
    nb_voitures = voitures.count()
    nb_reservations = reservations.count()
    top5 = voitures[:5]
    return render(request, 'location/dashboard.html', {
        'voitures': voitures,
        'reservations': reservations,
        'nb_voitures': nb_voitures,
        'nb_reservations': nb_reservations,
        'top5': top5,
    })


# ---- HELPERS ----------------------------------------------------------
def is_proprietaire(user):
    return user.is_authenticated and user.type_utilisateur in ('proprietaire', 'admin')


# ---- ADMIN : CRÉER UN PROPRIÉTAIRE ----------------------------------
@user_passes_test(is_admin, login_url='/connexion/')
def admin_creer_proprietaire(request):
    from .forms import CreerProprietaireForm
    form = CreerProprietaireForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Compte propriétaire créé pour {user.get_full_name()} ({user.email})')
        return redirect('dashboard')
    proprietaires = Utilisateur.objects.filter(type_utilisateur='proprietaire').order_by('-date_inscription')
    return render(request, 'location/admin_creer_proprietaire.html', {
        'form': form,
        'proprietaires': proprietaires,
    })


@user_passes_test(is_admin, login_url='/connexion/')
def admin_supprimer_proprietaire(request, pk):
    user = get_object_or_404(Utilisateur, pk=pk, type_utilisateur='proprietaire')
    if request.method == 'POST':
        nom = user.get_full_name()
        user.delete()
        messages.success(request, f'Compte de {nom} supprimé.')
    return redirect('admin_creer_proprietaire')


# ----- ESPACE PROPRIÉTAIRE --------------------------------------------------------------
@user_passes_test(is_proprietaire, login_url='/connexion/')
def proprio_dashboard(request):
    voitures = Voiture.objects.filter(proprietaire=request.user).order_by('-nb_locations')
    reservations = Reservation.objects.filter(
        voiture__proprietaire=request.user
    ).select_related('utilisateur', 'voiture').order_by('-date_reservation')
    return render(request, 'location/proprio_dashboard.html', {
        'voitures': voitures,
        'reservations': reservations,
        'nb_voitures': voitures.count(),
        'nb_reservations': reservations.count(),
    })


@user_passes_test(is_proprietaire, login_url='/connexion/')
def proprio_ajouter_voiture(request):
    from .forms import VoitureForm
    form = VoitureForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        v = form.save(commit=False)
        v.proprietaire = request.user
        v.save()
        messages.success(request, f'{v.marque} {v.modele} ajouté avec succès.')
        return redirect('proprio_dashboard')
    return render(request, 'location/proprio_voiture_form.html', {'form': form, 'action': 'Ajouter'})


@user_passes_test(is_proprietaire, login_url='/connexion/')
def proprio_modifier_voiture(request, pk):
    from .forms import VoitureForm
    voiture = get_object_or_404(Voiture, pk=pk) #proprietaire=request.user)
    form = VoitureForm(request.POST or None, request.FILES or None, instance=voiture)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Véhicule mis à jour.')
        return redirect('proprio_dashboard')
    return render(request, 'location/proprio_voiture_form.html', {'form': form, 'action': 'Modifier', 'voiture': voiture})


@user_passes_test(is_proprietaire, login_url='/connexion/')
def proprio_supprimer_voiture(request, pk):
    voiture = get_object_or_404(Voiture, pk=pk, proprietaire=request.user)
    if request.method == 'POST':
        nom = f'{voiture.marque} {voiture.modele}'
        voiture.delete()
        messages.success(request, f'{nom} supprimé.')
    return redirect('proprio_dashboard')


@user_passes_test(is_proprietaire, login_url='/connexion/')
def proprio_changer_statut_resa(request, pk):
    """Permet au proprio de confirmer / annuler une réservation sur ses voitures."""
    reservation = get_object_or_404(Reservation, pk=pk, voiture__proprietaire=request.user)
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        choix_valides = [s for s, _ in reservation._meta.get_field('statut_reservation').choices]
        if nouveau_statut in choix_valides:
            reservation.statut_reservation = nouveau_statut
            reservation.save()
            messages.success(request, f'Statut mis à jour : {nouveau_statut}')
    return redirect('proprio_dashboard')
