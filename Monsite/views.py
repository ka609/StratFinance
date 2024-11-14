from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from .models import Investissement, Niveau, Transaction,ProfilUtilisateur,Paramètres
from .forms import InvestissementForm,InscriptionForm,CompleterProfilForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.conf import settings
from cinetpay_sdk.s_d_k import Cinetpay
from decouple import config
import uuid
from django.utils import timezone 


def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue.")
            return redirect('Monsite:completer_profil')
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()
    return render(request, 'inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {username}!")
                return redirect('Monsite:accueil')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Erreur dans le formulaire de connexion.")
    else:
        form = AuthenticationForm()
    return render(request, 'connexion.html', {'form': form})


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('Monsite:accueil')


# Page d'accueil
def accueil(request):
    niveaux = Niveau.objects.all()
    niveaux_avec_gain_total = []

    # Calcul du gain total pour chaque niveau
    for niveau in niveaux:
        gain_total = niveau.montant_min * (niveau.pourcentage_gain_journalier / 100) * niveau.duree
        niveaux_avec_gain_total.append({
            'niveau': niveau,
            'gain_total': gain_total
        })

    # Initialiser les variables pour les utilisateurs non connectés
    investissement_actuel = None
    message_motivation = None

    # Vérifier si l'utilisateur est connecté
    if request.user.is_authenticated:
        # Récupérer l'investissement actif de l'utilisateur
        try:
            investissement_actuel = Investissement.objects.get(utilisateur=request.user, actif=True)
            niveau = investissement_actuel.niveau
            profil = ProfilUtilisateur.objects.get(utilisateur=request.user)

            # Calculer le gain quotidien basé sur le pourcentage
            gain_journalier = investissement_actuel.montant * (niveau.pourcentage_gain_journalier / 100)

            # Vérifier si le gain quotidien a déjà été ajouté aujourd'hui
            derniere_mise_a_jour = investissement_actuel.date_depot
            if derniere_mise_a_jour.date() < timezone.now().date():
                # Ajouter le gain quotidien au solde de l'utilisateur
                profil.solde += gain_journalier
                profil.save()

                # Mettre à jour la date du dépôt pour enregistrer le dernier ajout
                investissement_actuel.date_depot = timezone.now()
                investissement_actuel.save()

        except Investissement.DoesNotExist:
            investissement_actuel = None
    else:
        # Message motivant pour les utilisateurs non connectés
        message_motivation = "Inscrivez-vous dès maintenant et commencez à gagner avec nos niveaux d'investissement !"

    # Passer les données au contexte
    context = {
        'niveaux_avec_gain_total': niveaux_avec_gain_total,
        'investissement_actuel': investissement_actuel,
        'message_motivation': message_motivation,
    }
    return render(request, 'accueil.html', context)


@login_required
def liste_investissements(request):
    investissements = Investissement.objects.filter(utilisateur=request.user)
    return render(request, 'investissements/liste_investissements.html', {'investissements': investissements})


# Création d'un nouvel investissement
@login_required
def creer_investissement(request):
    if request.method == 'POST':
        form = InvestissementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_investissements')
    else:
        form = InvestissementForm()

    return render(request, 'investissements/creer_investissement.html', {'form': form})


# Générer une transaction de type dépôt
@login_required
def creer_transaction(request, investissement_id):
    investissement = Investissement.objects.get(id=investissement_id)
    if request.method == 'POST':
        montant = investissement.montant
        Transaction.objects.create(
            investissement=investissement,
            utilisateur=request.user,
            montant=montant,
            type_transaction='depot'
        )
        return redirect('liste_investissements')

    return render(request, 'investissements/creer_transaction.html', {'investissement': investissement})

@login_required
def inviter_amis(request):
    # Générer un lien d'invitation unique (par exemple en utilisant l'ID utilisateur)
    lien_invitation = request.build_absolute_uri(f"/inscription/?parrain_id={request.user.id}")

    return render(request, 'inviter_amis.html', {'lien_invitation': lien_invitation})


@login_required
def portefeuille(request):
    # Obtenez les informations de l'utilisateur, des investissements, et des transactions
    utilisateur = request.user
    investissements = Investissement.objects.filter(utilisateur=utilisateur)
    solde = sum(t.montant for t in Transaction.objects.filter(utilisateur=utilisateur, type_transaction='depot'))
    gain_journalier = sum(i.niveau.pourcentage_gain_journalier * i.montant / 100 for i in investissements if i.actif)
    nombre_parrains = utilisateur.filleuls.count()  # Utilisation correcte de related_name
    gain_reseau = sum(t.montant for t in Transaction.objects.filter(utilisateur=utilisateur, type_transaction='commission'))

    context = {
        'solde': solde,
        'gain_journalier': gain_journalier,
        'nombre_parrains': nombre_parrains,
        'gain_reseau': gain_reseau,
    }
    return render(request, 'portefeuille.html', context)

@login_required
def depot(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        if montant:
            Transaction.objects.create(
                utilisateur=request.user,
                montant=montant,
                type_transaction='depot'
            )
            messages.success(request, 'Votre dépôt a été effectué avec succès.')
            return redirect('Monsite:portefeuille')
    return render(request, 'depot.html')

@login_required
def retrait(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        if montant:
            Transaction.objects.create(
                utilisateur=request.user,
                montant=montant,
                type_transaction='retrait'
            )
            messages.success(request, 'Votre demande de retrait a été soumise avec succès.')
            return redirect('Monsite:portefeuille')
    return render(request, 'retrait.html')

# views.py

@login_required
def assistance(request):
    return render(request, 'assistance.html')

@login_required
def historique_transactions(request):
    transactions = Transaction.objects.filter(utilisateur=request.user).order_by('-date')
    context = {
        'transactions': transactions,
    }
    return render(request, 'historique_transactions.html', context)

@login_required
def activer_niveau(request, niveau_id):
    niveau = get_object_or_404(Niveau, id=niveau_id)

    if request.method == 'POST':
        montant = niveau.montant_min  # Montant requis pour activer ce niveau

        # Création d'un investissement avec le montant requis
        investissement = Investissement.objects.create(
            utilisateur=request.user,
            niveau=niveau,
            montant=montant,
            actif=True
        )

        messages.success(request, f'Le niveau {niveau.nom} a été activé avec succès !')
        return redirect('Monsite:portefeuille')

    context = {
        'niveau': niveau,
    }
    return render(request, 'activer_niveau.html', context)

@login_required
def deposer_fonds(request):
    # Récupérer les paramètres CinetPay depuis le modèle Paramètres
    params = get_object_or_404(Paramètres)  # Récupère l'unique instance de Paramètres, sinon 404

    if request.method == 'POST':
        montant = request.POST.get('montant')

        # Initialiser le client Cinetpay avec les valeurs issues de Paramètres
        client = Cinetpay(params.CINETPAY_APIKEY, params.CINETPAY_SITE_ID)

        # Générer un ID de transaction unique
        transaction_id = str(uuid.uuid4())

        data = {
            'amount': montant,
            'currency': "XOF",
            'transaction_id': transaction_id,
            'description': "Dépôt de fonds sur la plateforme",
            'return_url': "http://127.0.0.1:8000/paiement_succes/",
            'notify_url': "http://127.0.0.1:8000/paiement_notification/",
            'customer_name': request.user.first_name,
            'customer_surname': request.user.last_name,
        }

        try:
            response = client.PaymentInitialization(data)
            print(response)
            # Vérification du code de succès et extraction de l'URL de paiement
            if response.get("code") == "201":
                payment_url = response["data"].get("payment_url")
                if payment_url:
                    # Enregistrer la transaction en attente
                    Transaction.objects.create(
                        utilisateur=request.user,
                        montant=montant,
                        type_transaction='depot',
                        investissement=None  # Mettre à jour si nécessaire
                    )
                    # Rediriger vers l'URL de paiement
                    return redirect(payment_url)
                else:
                    return render(request, 'paiement_erreur.html', {"message": "URL de paiement introuvable dans la réponse."})
            else:
                return render(request, 'paiement_erreur.html', {"message": response.get("message")})
        except Exception as e:
            return render(request, 'paiement_erreur.html', {"message": str(e)})

    return render(request, 'deposer_fonds.html')

@login_required
def verifier_depot(request, transaction_id):
    client = Cinetpay(settings.CINETPAY_APIKEY, settings.CINETPAY_SITE_ID)

    try:
        response = client.TransactionVerfication_trx(transaction_id)
        if response.get("status") == "success":
            # Mettre à jour la transaction comme validée
            Transaction.objects.filter(
                utilisateur=request.user,
                montant=response["amount"],
                type_transaction='depot',
                date__date=date.today()  # Assurez-vous que la date correspond
            ).update(status='completed')  # Ajouter le champ status si besoin

            return render(request, 'depot_succes.html', {"details": response})
        else:
            return render(request, 'depot_echec.html', {"message": response.get("message")})
    except Exception as e:
        return render(request, 'depot_erreur.html', {"message": str(e)})



def notification_depot(request):
    transaction_id = request.GET.get("transaction_id")
    client = Cinetpay(settings.CINETPAY_APIKEY, settings.CINETPAY_SITE_ID)

    response = client.TransactionVerfication_trx(transaction_id)
    if response.get("status") == "success":
        # Marquer la transaction comme réussie
        Transaction.objects.filter(transaction_id=transaction_id, type_transaction='depot').update(status='completed')

    return HttpResponse(status=200)


@login_required
def retirer_fonds(request):
    utilisateur = request.user
    profil = get_object_or_404(ProfilUtilisateur, utilisateur=utilisateur)

    if request.method == 'POST':
        montant = float(request.POST.get('montant'))

        # Vérifier si l'utilisateur a un solde suffisant pour le retrait
        if profil.solde >= montant:
            profil.solde -= montant  # Déduire le montant du solde
            profil.save()

            # Enregistrer la transaction de retrait
            Transaction.objects.create(
                utilisateur=utilisateur,
                montant=montant,
                type_transaction='retrait'
            )

            return redirect('page_succes')  # Rediriger vers une page de succès de retrait
        else:
            return render(request, 'retirer_fonds.html', {'message': "Solde insuffisant pour ce retrait."})

    return render(request, 'retirer_fonds.html')


def paiement_succes(request):
    return render(request, 'paiement_succes.html', {'message': 'Votre paiement a été effectué avec succès.'})


def paiement_notification(request):
    transaction_id = request.GET.get('transaction_id')

    client = Cinetpay(CINETPAY_API_KEY, CINETPAY_SITE_ID)
    response = client.TransactionVerfication_trx(transaction_id)

    if response.get('status') == 'SUCCESS':
        # Marquer la transaction comme complétée dans votre base de données
        return HttpResponse("Notification reçue avec succès", status=200)
    else:
        return HttpResponse("Erreur dans la notification", status=400)


# Vue pour afficher une erreur de paiement
def paiement_erreur(request):
    message = "Une erreur s'est produite lors de votre paiement."
    return render(request, 'paiement_erreur.html', {'message': message})


# Charger les informations d'API depuis les variables d'environnement
CINETPAY_API_KEY = config('CINETPAY_API_KEY')
CINETPAY_SITE_ID = config('CINETPAY_SITE_ID')


def initier_paiement(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        transaction_id = "123456789"  # Remplacez par une logique pour générer un ID unique de transaction

        # Initialiser le client CinetPay
        client = Cinetpay(CINETPAY_API_KEY, CINETPAY_SITE_ID)

        # Créer les données pour l'initialisation du paiement
        data = {
            'amount': montant,
            'currency': "XOF",
            'transaction_id': transaction_id,
            'description': "Paiement pour l'investissement",
            'return_url': "http://127.0.0.1:8000/paiement_succes/",
            'notify_url': "http://127.0.0.1:8000/paiement_notification/",
            'customer_name': request.user.first_name,
            'customer_surname': request.user.last_name,
        }

        # Envoyer la requête de paiement
        response = client.PaymentInitialization(data)
        if response.get('status') == 'ACCEPTED':
            return redirect(response['payment_url'])  # Redirige vers la page de paiement CinetPay
        else:
            return render(request, 'paiement_erreur.html',
                          {'message': response.get('message', 'Erreur lors de l\'initialisation du paiement')})

    return render(request, 'initier_paiement.html')


@login_required
def completer_profil(request):
    if request.method == 'POST':
        form = CompleterProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour !")
            return redirect('Monsite:accueil')  # Redirection vers le tableau de bord après mise à jour
        else:
            messages.error(request, "Erreur lors de la mise à jour des informations.")
    else:
        form = CompleterProfilForm(instance=request.user)

    return render(request, 'completer_profil.html', {'form': form})


@login_required
def profil_utilisateur(request):
    utilisateur = request.user  # Utilisateur connecté
    return render(request, 'profil_utilisateur.html', {'utilisateur': utilisateur})
