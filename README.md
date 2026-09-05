# SahelRide – Location de voitures au Burkina Faso

## Installation rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Appliquer les migrations
python manage.py migrate

# 3. Créer le superadmin
python manage.py createsuperuser

# 4. Lancer le serveur
python manage.py runserver
```

## Accès par défaut (données de démo)
- **Site** : http://127.0.0.1:8000/
- **Dashboard admin** : http://127.0.0.1:8000/dashboard/
  - Email : admin@sahelride.bf
  - Mot de passe : admin1234
- **Admin Django** : http://127.0.0.1:8000/admin/

## Ajouter une image à un véhicule
1. Déposez votre image dans le dossier `media/voitures/`
2. Dans l'admin Django (`/admin/location/voiture/`), éditez le véhicule et sélectionnez l'image.

## Structure du projet
```
sahelride/
├── sahelride/          → Configuration Django (settings, urls)
├── location/           → App principale
│   ├── models.py       → Utilisateur, Voiture, Reservation, Paiement, Avis
│   ├── views.py        → Toutes les vues
│   ├── forms.py        → Formulaires
│   ├── urls.py         → Routes
│   ├── templates/      → HTML (base.html + toutes les pages)
│   └── static/         → CSS (styles.css) + JS (nav.js)
├── media/voitures/     → Images des véhicules (à déposer ici)
├── requirements.txt
└── manage.py
```

## Pages disponibles
| URL | Page |
|-----|------|
| `/` | Accueil |
| `/voitures/` | Toutes les voitures |
| `/voitures/<id>/` | Détail d'un véhicule |
| `/par-ville/` | Filtrer par ville |
| `/inscription/` | Créer un compte |
| `/connexion/` | Se connecter |
| `/reserver/<id>/` | Formulaire de réservation |
| `/paiement/<id>/` | Paiement (Orange Money, Moov, etc.) |
| `/mes-reservations/` | Historique client |
| `/contact/` | Formulaire de contact |
| `/dashboard/` | Dashboard admin uniquement |
