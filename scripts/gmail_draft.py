import base64
import os
from email.mime.text import MIMEText
from scripts.gmail_auth import get_gmail_service

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def creer_brouillon(destinataire, entreprise, poste, type_relance):
    service = get_gmail_service()

    if type_relance == "1":
        objet = f"Relance candidature — {poste} chez {entreprise}"
        corps = (
            f"Bonjour,\n\n"
            f"Je me permets de revenir vers vous concernant ma candidature au poste de {poste} "
            f"au sein de {entreprise}, envoyée il y a quelques jours.\n\n"
            f"Je reste très motivé(e) par cette opportunité et serais ravi(e) de pouvoir échanger avec vous.\n\n"
            f"Dans l'attente de votre retour, je reste disponible pour tout complément d'information.\n\n"
            f"Cordialement,"
        )
    else:
        objet = f"Relance candidature — {poste} chez {entreprise}"
        corps = (
            f"Bonjour,\n\n"
            f"Je me permets de vous recontacter au sujet de ma candidature au poste de {poste} chez {entreprise}.\n\n"
            f"Toujours très intéressé(e) par ce poste, je serais heureux(se) de pouvoir en discuter avec vous.\n\n"
            f"Cordialement,"
        )

    message = MIMEText(corps)
    message["to"] = destinataire if destinataire else ""
    message["subject"] = objet

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    brouillon = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}}
    ).execute()

    return brouillon["id"]
