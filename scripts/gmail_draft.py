import base64
import os
from email.mime.text import MIMEText
from scripts.gmail_auth import get_gmail_service

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def creer_brouillon(destinataire, entreprise, poste, type_relance):
    service = get_gmail_service()

    # Objet de l'email
    if type_relance == "1":
        objet = f"Relance candidature — {poste} chez {entreprise}"
        corps = f"""Bonjour,

Je me permets de revenir vers vous concernant ma candidature au poste de {poste} au sein de {entreprise}, envoyée il y a quelques jours.

Je reste très motivé(e) par cette opportunité et serais ravi(e) de pouvoir échanger avec vous à ce sujet.

Dans l'attente de votre retour, je reste disponible pour tout complément d'information.

Cordialement,"""
    else:
        objet = f"Relance candidature — {poste} chez {entreprise}"
        corps = f"""Bonjour,

Je me permets de vous recontacter au sujet de ma candidature au poste de {poste} chez {entreprise}.

Toujours très intéressé(e) par ce poste, je serais heureux(se) de pouvoir en discuter avec vous.

Cordialement,"""

    # Création du message
    message = MIMEText(corps)
    message["to"] = destinataire if destinataire else ""
    message["subject"] = objet

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    brouillon = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    return brouillon["id"]