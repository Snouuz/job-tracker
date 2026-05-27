from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime, date, timedelta
from scripts.gmail_draft import creer_brouillon

app = Flask(__name__, template_folder="dashboard")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "candidatures.csv")


# ─── Helpers ───────────────────────────────────────────────

def lire_candidatures():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_next_id(candidatures):
    if not candidatures:
        return 1
    return max(int(c["id"]) for c in candidatures) + 1


def calculer_stats(candidatures):
    total = len(candidatures)
    entretiens = sum(1 for c in candidatures if c["statut"] == "entretien")
    refus = sum(1 for c in candidatures if c["statut"] == "refus")
    en_attente = sum(1 for c in candidatures if c["statut"] in ["envoyée", "relance_1", "relance_2"])
    taux = round(((entretiens + refus) / total * 100)) if total > 0 else 0
    return {"total": total, "entretiens": entretiens, "refus": refus, "en_attente": en_attente, "taux_reponse": taux}


def calculer_relances(candidatures):
    aujourd_hui = date.today()
    relances = []
    statuts_exclus = ["refus", "acceptée", "entretien"]

    for c in candidatures:
        if c["statut"] in statuts_exclus:
            continue

        # Relance J+2
        if c["relance_1_faite"] == "False" and c["date_relance_1"]:
            if date.fromisoformat(c["date_relance_1"]) <= aujourd_hui:
                relances.append({**c, "type_relance": "Relance J+2"})

        # Relance J+5
        if c["relance_2_faite"] == "False" and c["date_relance_2"]:
            if date.fromisoformat(c["date_relance_2"]) <= aujourd_hui:
                relances.append({**c, "type_relance": "Relance J+5"})

    return relances


# ─── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    candidatures = lire_candidatures()
    return render_template(
        "template.html",
        candidatures=candidatures,
        stats=calculer_stats(candidatures),
        relances=calculer_relances(candidatures),
        date_generation=datetime.now().strftime("%d/%m/%Y à %Hh%M"),
    )


@app.route("/ajouter", methods=["POST"])
def ajouter():
    candidatures = lire_candidatures()
    aujourd_hui = date.today()

    nouvelle = {
        "id":               get_next_id(candidatures),
        "entreprise":       request.form.get("entreprise", "").strip(),
        "poste":            request.form.get("poste", "").strip(),
        "date_candidature": aujourd_hui,
        "canal":            request.form.get("canal", "").strip(),
        "statut":           "envoyée",
        "email_contact":    request.form.get("email_contact", "").strip(),
        "lien":             request.form.get("lien", "").strip(),
        "notes":            request.form.get("notes", "").strip(),
        "date_relance_1":   aujourd_hui + timedelta(days=2),
        "date_relance_2":   aujourd_hui + timedelta(days=5),
        "relance_1_faite":  "False",
        "relance_2_faite":  "False",
    }

    # Saut de ligne propre avant écriture
    with open(CSV_PATH, "rb+") as f:
        f.seek(-1, 2)
        if f.read(1) != b"\n":
            f.write(b"\n")

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=nouvelle.keys())
        writer.writerow(nouvelle)

    return redirect(url_for("index"))


@app.route("/relance/<int:cid>/<int:num>")
def marquer_relance(cid, num):
    candidatures = lire_candidatures()
    for c in candidatures:
        if int(c["id"]) == cid:
            if num == 1:
                # Toggle
                c["relance_1_faite"] = "False" if c["relance_1_faite"] == "True" else "True"
                c["statut"] = "relance_1" if c["relance_1_faite"] == "True" else "envoyée"
            elif num == 2:
                c["relance_2_faite"] = "False" if c["relance_2_faite"] == "True" else "True"
                c["statut"] = "relance_2" if c["relance_2_faite"] == "True" else "relance_1"

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=candidatures[0].keys())
        writer.writeheader()
        writer.writerows(candidatures)

    return redirect(url_for("index"))


@app.route("/supprimer/<int:cid>")
def supprimer(cid):
    candidatures = lire_candidatures()
    candidatures = [c for c in candidatures if int(c["id"]) != cid]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        if candidatures:
            writer = csv.DictWriter(f, fieldnames=candidatures[0].keys())
            writer.writeheader()
            writer.writerows(candidatures)
        else:
            # Si plus aucune candidature, on remet juste l'en-tête
            writer = csv.writer(f)
            writer.writerow([
                "id", "entreprise", "poste", "date_candidature", "canal", "statut",
                "email_contact", "lien", "notes", "date_relance_1", "date_relance_2",
                "relance_1_faite", "relance_2_faite"
            ])

    return redirect(url_for("index"))


@app.route("/statut/<int:cid>", methods=["POST"])
def modifier_statut(cid):
    candidatures = lire_candidatures()
    for c in candidatures:
        if int(c["id"]) == cid:
            c["statut"] = request.form.get("statut")

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=candidatures[0].keys())
        writer.writeheader()
        writer.writerows(candidatures)

    return redirect(url_for("index"))


@app.route("/brouillon/<int:cid>/<int:num>")
def creer_brouillon_route(cid, num):
    candidatures = lire_candidatures()
    candidature = next((c for c in candidatures if int(c["id"]) == cid), None)

    if not candidature:
        return redirect(url_for("index"))

    creer_brouillon(
        destinataire=candidature["email_contact"],
        entreprise=candidature["entreprise"],
        poste=candidature["poste"],
        type_relance=str(num)
    )

    return redirect(url_for("index"))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
