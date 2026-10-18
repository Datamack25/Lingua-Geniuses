"""Notifications intelligentes (in-app) + envoi e-mail optionnel (SMTP via st.secrets)."""
from __future__ import annotations
import smtplib, ssl
from email.message import EmailMessage
from datetime import date
import pandas as pd
from . import storage as S
from . import gamification as G
from . import ml_engine as ML


def push(user_id: str, kind: str, title: str, body: str) -> None:
    S.append("notifications", dict(ts=S.now(), user_id=user_id, kind=kind, title=title, body=body, read="0"))


def _sent_today(user_id: str, kind: str) -> bool:
    n = S.user_rows("notifications", user_id)
    if n.empty:
        return False
    n = n[(n.kind == kind) & (pd.to_datetime(n.ts, errors="coerce").dt.date == date.today())]
    return not n.empty


def generate(user_id: str, lang: str, lang_name: str) -> None:
    """Règles de coaching (agent Lumi) : une notification max par type et par jour."""
    att = S.user_rows("attempts", user_id, lang)
    diags = S.user_rows("diagnostics", user_id, lang)
    if diags.empty and not _sent_today(user_id, f"diag_{lang}"):
        push(user_id, f"diag_{lang}", f"🧭 Diagnostic {lang_name} disponible",
             "Atlas vous attend : 12 questions adaptatives pour situer votre niveau CECRL.")
    if G.streak(user_id) >= 1 and G.xp_today(user_id) == 0 and not _sent_today(user_id, "streak"):
        push(user_id, "streak", "🔥 Votre série est en jeu !",
             f"Vous avez une série de {G.streak(user_id)} jour(s). 5 minutes suffisent pour la prolonger.")
    m = ML.skill_mastery(att)
    if m:
        weak = min(m, key=m.get)
        if m[weak] < .6 and not _sent_today(user_id, f"weak_{lang}"):
            push(user_id, f"weak_{lang}", f"🎯 Point à renforcer : {S.SKILLS[weak]}",
                 f"Votre maîtrise en {S.SKILLS[weak].lower()} ({lang_name}) est de {round(m[weak]*100)} %. "
                 "Une session ciblée vous attend chez l'agent concerné.")
    if not att.empty:
        wrong = att[att.correct == "0"]
        if len(wrong) >= 3 and not _sent_today(user_id, f"review_{lang}"):
            push(user_id, f"review_{lang}", "🔁 Révision espacée prête",
                 f"{len(wrong)} items ratés sont prêts à être revus : c'est le meilleur moment pour les ancrer.")
    if not diags.empty:
        lvl = diags.iloc[-1].level
        has_cert = not S.user_rows("certificates", user_id, lang).query("level == @lvl").empty
        if not has_cert and not _sent_today(user_id, f"cert_{lang}"):
            push(user_id, f"cert_{lang}", f"🎓 Certificat {lvl} accessible",
                 f"Passez l'évaluation certifiante {lang_name} {lvl} pour obtenir votre certificat PDF.")


def unread(user_id: str) -> pd.DataFrame:
    n = S.user_rows("notifications", user_id)
    return n[n.read == "0"]


def mark_all_read(user_id: str) -> None:
    n = S.read("notifications")
    n.loc[n.user_id == user_id, "read"] = "1"
    S.write("notifications", n)


def send_email(cfg: dict, to: str, subject: str, body: str) -> tuple[bool, str]:
    """cfg = st.secrets['smtp'] : host, port, user, password, sender."""
    try:
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = cfg["sender"], to, subject
        msg.set_content(body)
        with smtplib.SMTP(cfg["host"], int(cfg.get("port", 587))) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(cfg["user"], cfg["password"])
            s.send_message(msg)
        return True, "E-mail envoyé."
    except Exception as e:  # noqa: BLE001
        return False, f"Envoi impossible : {e}"
