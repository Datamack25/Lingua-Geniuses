"""XP, séries (streaks), badges, quêtes du jour, messages bienveillants."""
from __future__ import annotations
import math, random
from datetime import date, timedelta
import pandas as pd
from . import storage as S

XP = dict(correct=10, wrong=3, diagnostic=80, writing=40, story=20, culture=15, arcade=25, exam=150, quest=50)

ENCOURAGE_OK = ["Bravo ! 🎉", "Excellent, continuez comme ça ! 🚀", "Parfait ! Votre cerveau vous remercie 🧠",
                "Superbe réponse ✨", "Vous progressez à vue d'œil 🌱", "Magnifique ! 🌟"]
ENCOURAGE_KO = ["Pas grave : chaque erreur est une marche vers la réussite 💪",
                "Presque ! Lisez l'explication, vous l'aurez la prochaine fois 🌱",
                "On apprend surtout de ses erreurs — courage ! 🤝",
                "Belle tentative ! Nova vous proposera cet item à nouveau bientôt 🔁"]


def cheer(ok: bool) -> str:
    return random.choice(ENCOURAGE_OK if ok else ENCOURAGE_KO)


def add_xp(user_id: str, xp: int, reason: str, lang: str = "") -> None:
    S.append("xp_log", dict(ts=S.now(), user_id=user_id, xp=str(xp), reason=reason, lang=lang))


def total_xp(user_id: str) -> int:
    d = S.user_rows("xp_log", user_id)
    return int(pd.to_numeric(d.xp, errors="coerce").fillna(0).sum()) if not d.empty else 0


def player_level(xp: int) -> tuple[int, int, int]:
    """Niveau joueur (courbe racine) : retourne (niveau, xp dans le niveau, xp requis)."""
    lvl = int(math.sqrt(xp / 100)) + 1
    base = 100 * (lvl - 1) ** 2
    nxt = 100 * lvl ** 2
    return lvl, xp - base, nxt - base


def streak(user_id: str) -> int:
    d = S.user_rows("xp_log", user_id)
    if d.empty:
        return 0
    days = set(pd.to_datetime(d.ts, errors="coerce").dt.date.dropna())
    s, cur = 0, date.today()
    if cur not in days:
        cur -= timedelta(days=1)          # la série reste valable jusqu'à la fin de la journée
    while cur in days:
        s += 1
        cur -= timedelta(days=1)
    return s


def xp_today(user_id: str) -> int:
    d = S.user_rows("xp_log", user_id)
    if d.empty:
        return 0
    t = pd.to_datetime(d.ts, errors="coerce").dt.date == date.today()
    return int(pd.to_numeric(d[t].xp, errors="coerce").sum())


def daily_quests(user_id: str) -> list[dict]:
    d = S.user_rows("xp_log", user_id)
    today = d[pd.to_datetime(d.ts, errors="coerce").dt.date == date.today()] if not d.empty else d
    reasons = list(today.reason) if not today.empty else []
    return [
        dict(icon="🎯", label="Répondre à 10 exercices", done=sum(r in ("correct", "wrong") for r in reasons) >= 10,
             progress=min(10, sum(r in ("correct", "wrong") for r in reasons)), goal=10),
        dict(icon="🎭", label="Explorer 1 contenu culturel", done=any(r in ("culture", "story") for r in reasons),
             progress=int(any(r in ("culture", "story") for r in reasons)), goal=1),
        dict(icon="✍️", label="Faire analyser 1 texte", done="writing" in reasons,
             progress=int("writing" in reasons), goal=1),
    ]


def badges(user_id: str) -> list[str]:
    got = []
    xp = total_xp(user_id)
    st = streak(user_id)
    diags = S.user_rows("diagnostics", user_id)
    if not diags.empty:
        got.append("first_step")
    if diags.lang.nunique() >= 3 if not diags.empty else False:
        got.append("polyglot")
    if st >= 3: got.append("streak_3")
    if st >= 7: got.append("streak_7")
    if xp >= 500: got.append("xp_500")
    if xp >= 2000: got.append("xp_2000")
    if len(S.user_rows("writings", user_id)) >= 5: got.append("writer")
    if not S.user_rows("certificates", user_id).empty: got.append("certified")
    log = S.user_rows("xp_log", user_id)
    if not log.empty and (log.reason.isin(["culture", "story"])).sum() >= 10: got.append("culture")
    att = S.user_rows("attempts", user_id)
    if not att.empty:
        run = best = 0
        for c in att.correct:
            run = run + 1 if c == "1" else 0
            best = max(best, run)
        if best >= 10: got.append("perfect")
    return got


def leaderboard(limit: int = 10) -> pd.DataFrame:
    log = S.read("xp_log")
    users = S.read("users")[["user_id", "display_name"]]
    if log.empty:
        return pd.DataFrame(columns=["Joueur", "XP"])
    log["xp"] = pd.to_numeric(log.xp, errors="coerce")
    week = log[pd.to_datetime(log.ts, errors="coerce") >= pd.Timestamp.now() - pd.Timedelta(days=7)]
    lb = week.groupby("user_id").xp.sum().reset_index().merge(users, on="user_id", how="left")
    lb = lb.sort_values("xp", ascending=False).head(limit)
    return lb.rename(columns={"display_name": "Joueur", "xp": "XP"})[["Joueur", "XP"]]
