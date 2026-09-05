from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Utilisateur, Reservation, Paiement, Avis


class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Mot de passe'}))
    password2 = forms.CharField(label='Confirmer', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirmer le mot de passe'}))

    class Meta:
        model = Utilisateur
        fields = ['nom','prenom','email','telephone']
        widgets = {
            'nom': forms.TextInput(attrs={'class':'form-control','placeholder':'Nom'}),
            'prenom': forms.TextInput(attrs={'class':'form-control','placeholder':'Prénom(s)'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder':'Adresse email'}),
            'telephone': forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone (ex: +226 70 00 00 00)'}),
        }

    def clean(self):
        cd = super().clean()
        if cd.get('password1') != cd.get('password2'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Adresse email','autofocus':True}))
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Mot de passe'}))


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_debut','date_fin']
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_fin': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_debut'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_fin'].input_formats = ['%Y-%m-%dT%H:%M']


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['mode_paiement']
        widgets = {
            'mode_paiement': forms.RadioSelect(attrs={'class':'form-check-input'}),
        }


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note','commentaire']
        widgets = {
            'note': forms.Select(choices=[(i,f'{i} étoile{"s" if i>1 else ""}') for i in range(1,6)], attrs={'class':'form-select'}),
            'commentaire': forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Partagez votre expérience...'}),
        }


class ContactForm(forms.Form):
    nom = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Votre nom'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Votre email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows':5,'placeholder':'Votre message...'}))


class CreerProprietaireForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Mot de passe'}))
    password2 = forms.CharField(label='Confirmer', widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirmer'}))

    class Meta:
        model = Utilisateur
        fields = ['nom','prenom','email','telephone']
        widgets = {
            'nom': forms.TextInput(attrs={'class':'form-control','placeholder':'Nom'}),
            'prenom': forms.TextInput(attrs={'class':'form-control','placeholder':'Prénom(s)'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}),
            'telephone': forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone'}),
        }

    def clean(self):
        cd = super().clean()
        if cd.get('password1') != cd.get('password2'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type_utilisateur = 'proprietaire'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class VoitureForm(forms.ModelForm):
    class Meta:
        from .models import Voiture
        model = Voiture
        fields = ['marque','modele','annee','couleur','immatriculation','description',
                'disponibilite','prix_jour','caution','ville','adresse',
                'nombre_places','type_carburant','transmission','image']
        widgets = {
            'marque': forms.TextInput(attrs={'class':'form-control','placeholder':'Ex: Toyota'}),
            'modele': forms.TextInput(attrs={'class':'form-control','placeholder':'Ex: Land Cruiser'}),
            'annee': forms.NumberInput(attrs={'class':'form-control','placeholder':'Ex: 2022'}),
            'couleur': forms.TextInput(attrs={'class':'form-control','placeholder':'Ex: Blanc'}),
            'immatriculation': forms.TextInput(attrs={'class':'form-control','placeholder':'Ex: 11BF2201A'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Description du véhicule...'}),
            'disponibilite': forms.Select(attrs={'class':'form-select'}),
            'prix_jour': forms.NumberInput(attrs={'class':'form-control','placeholder':'Ex: 50000'}),
            'caution': forms.NumberInput(attrs={'class':'form-control','placeholder':'Ex: 100000'}),
            'ville': forms.Select(attrs={'class':'form-select'}),
            'adresse': forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse exacte'}),
            'nombre_places': forms.NumberInput(attrs={'class':'form-control'}),
            'type_carburant': forms.TextInput(attrs={'class':'form-control','placeholder':'Essence / Diesel'}),
            'transmission': forms.TextInput(attrs={'class':'form-control','placeholder':'Manuelle / Automatique'}),
            'image': forms.ClearableFileInput(attrs={'class':'form-control'}),
        }
