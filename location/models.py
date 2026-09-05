from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('type_utilisateur', 'admin')
        return self.create_user(email, nom, prenom, password, **extra)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    TYPE_CHOICES = [('client','Client'),('proprietaire','Propriétaire'),('admin','Administrateur')]
    type_utilisateur = models.CharField(max_length=50, choices=TYPE_CHOICES, default='client')
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    date_inscription = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UtilisateurManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    def __str__(self): return f"{self.prenom} {self.nom}"
    def get_full_name(self): return f"{self.prenom} {self.nom}"


VILLES = [('Ouagadougou','Ouagadougou'),('Bobo-Dioulasso','Bobo-Dioulasso'),('Gaoua','Gaoua')]
DISPO = [('Disponible','Disponible'),('Indisponible','Indisponible')]


class Voiture(models.Model):
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='voitures')
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    annee = models.IntegerField(null=True, blank=True)
    couleur = models.CharField(max_length=30, blank=True)
    immatriculation = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    disponibilite = models.CharField(max_length=30, choices=DISPO, default='Disponible')
    prix_jour = models.DecimalField(max_digits=8, decimal_places=0)
    caution = models.DecimalField(max_digits=8, decimal_places=0, null=True, blank=True)
    ville = models.CharField(max_length=100, choices=VILLES)
    adresse = models.CharField(max_length=255)
    nombre_places = models.IntegerField(default=5)
    type_carburant = models.CharField(max_length=30, default='Essence')
    transmission = models.CharField(max_length=30, default='Manuelle')
    image = models.ImageField(upload_to='voitures/', null=True, blank=True)
    nb_locations = models.IntegerField(default=0)

    def __str__(self): return f"{self.marque} {self.modele} – {self.ville}"

    def note_moyenne(self):
        avis = self.avis_set.all()
        if avis.exists():
            return round(sum(a.note for a in avis) / avis.count(), 1)
        return None

    def image_url(self):
        if self.image and self.image.name:
            return self.image.url
        return '/static/location/img/car-placeholder.png'


class Avis(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    voiture = models.ForeignKey(Voiture, on_delete=models.CASCADE)
    note = models.IntegerField(default=5)
    commentaire = models.TextField()
    date_avis = models.DateField(default=timezone.now)
    class Meta: ordering = ['-date_avis']
    def __str__(self): return f"Avis de {self.utilisateur} sur {self.voiture}"


STATUT_RESA = [('En attente','En attente'),('Confirmée','Confirmée'),('En cours','En cours'),('Terminée','Terminée'),('Annulée','Annulée')]


class Reservation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.RESTRICT, related_name='reservations')
    voiture = models.ForeignKey(Voiture, on_delete=models.RESTRICT, related_name='reservations')
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    statut_reservation = models.CharField(max_length=30, choices=STATUT_RESA, default='En attente')
    date_reservation = models.DateTimeField(default=timezone.now)

    def __str__(self): return f"Réservation #{self.pk} – {self.utilisateur}"

    def nb_jours(self):
        delta = self.date_fin - self.date_debut
        return max(delta.days, 1)

    def save(self, *args, **kwargs):
        if not self.prix_total:
            delta = self.date_fin - self.date_debut
            jours = max(delta.days, 1)
            self.prix_total = self.voiture.prix_jour * jours
        super().save(*args, **kwargs)
        self._sync_disponibilite_voiture()  

    def _sync_disponibilite_voiture(self):
        now = timezone.now()
        voiture = self.voiture
        qs = Reservation.objects.filter(
            voiture=voiture,
            statut_reservation__in=['Confirmée', 'En cours'],
            date_fin__gte=now,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        active_ailleurs = qs.exists()
        self_bloque = (
            self.statut_reservation in ['Confirmée', 'En cours']
            and self.date_fin >= now
        )
        nouvelle_dispo = 'Indisponible' if (active_ailleurs or self_bloque) else 'Disponible'
        if voiture.disponibilite != nouvelle_dispo:
            Voiture.objects.filter(pk=voiture.pk).update(disponibilite=nouvelle_dispo)

    def get_statut_reservation_choices(self):
        return STATUT_RESA


MODE_PAIEMENT = [('Orange Money','Orange Money'),('Moov Money','Moov Money'),('Espèce','Espèce'),('Carte','Carte bancaire')]
ETAT_PAIEMENT = [('En attente','En attente'),('Validé','Validé'),('Échoué','Échoué')]


class Paiement(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='paiement')
    montant = models.DecimalField(max_digits=10, decimal_places=0)
    mode_paiement = models.CharField(max_length=50, choices=MODE_PAIEMENT)
    etat_paiement = models.CharField(max_length=30, choices=ETAT_PAIEMENT, default='En attente')
    date_paiement = models.DateTimeField(default=timezone.now)
    reference_transaction = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self): return f"Paiement #{self.pk}"
