
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('type_utilisateur', models.CharField(choices=[('client', 'Client'), ('proprietaire', 'Propriétaire'), ('admin', 'Administrateur')], default='client', max_length=50)),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('date_inscription', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut', models.DateTimeField()),
                ('date_fin', models.DateTimeField()),
                ('prix_total', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('statut_reservation', models.CharField(choices=[('En attente', 'En attente'), ('Confirmée', 'Confirmée'), ('En cours', 'En cours'), ('Terminée', 'Terminée'), ('Annulée', 'Annulée')], default='En attente', max_length=30)),
                ('date_reservation', models.DateTimeField(default=django.utils.timezone.now)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='reservations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=0, max_digits=10)),
                ('mode_paiement', models.CharField(choices=[('Orange Money', 'Orange Money'), ('Moov Money', 'Moov Money'), ('Espèce', 'Espèce'), ('Carte', 'Carte bancaire')], max_length=50)),
                ('etat_paiement', models.CharField(choices=[('En attente', 'En attente'), ('Validé', 'Validé'), ('Échoué', 'Échoué')], default='En attente', max_length=30)),
                ('date_paiement', models.DateTimeField(default=django.utils.timezone.now)),
                ('reference_transaction', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('reservation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='paiement', to='location.reservation')),
            ],
        ),
        migrations.CreateModel(
            name='Voiture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marque', models.CharField(max_length=50)),
                ('modele', models.CharField(max_length=50)),
                ('annee', models.IntegerField(blank=True, null=True)),
                ('couleur', models.CharField(blank=True, max_length=30)),
                ('immatriculation', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('disponibilite', models.CharField(choices=[('Disponible', 'Disponible'), ('Indisponible', 'Indisponible')], default='Disponible', max_length=30)),
                ('prix_jour', models.DecimalField(decimal_places=0, max_digits=8)),
                ('caution', models.DecimalField(blank=True, decimal_places=0, max_digits=8, null=True)),
                ('ville', models.CharField(choices=[('Ouagadougou', 'Ouagadougou'), ('Bobo-Dioulasso', 'Bobo-Dioulasso'), ('Gaoua', 'Gaoua')], max_length=100)),
                ('adresse', models.CharField(max_length=255)),
                ('nombre_places', models.IntegerField(default=5)),
                ('type_carburant', models.CharField(default='Essence', max_length=30)),
                ('transmission', models.CharField(default='Manuelle', max_length=30)),
                ('image', models.ImageField(blank=True, null=True, upload_to='voitures/')),
                ('nb_locations', models.IntegerField(default=0)),
                ('proprietaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voitures', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='reservation',
            name='voiture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='reservations', to='location.voiture'),
        ),
        migrations.CreateModel(
            name='Avis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.IntegerField(default=5)),
                ('commentaire', models.TextField()),
                ('date_avis', models.DateField(default=django.utils.timezone.now)),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('voiture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='location.voiture')),
            ],
            options={
                'ordering': ['-date_avis'],
            },
        ),
    ]
