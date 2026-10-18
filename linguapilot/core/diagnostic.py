"""
Diagnostic adaptatif (méthode de l'escalier / staircase, proche des tests de
positionnement informatisés) + évaluation certifiante.

- départ au niveau B1 ; bonne réponse → niveau supérieur, erreur → niveau inférieur
- rotation des compétences pour couvrir grammaire, vocabulaire, compréhension, registres, culture
- estimation finale = règle de seuil CECRL + classifieur RandomForest (ml_engine)
"""
from __future__ import annotations
import random
import numpy as np
import pandas as pd
from . import storage as S
from . import ml_engine as ML

N_DIAG = 12
USAGE = {
    "A1": "Débutant — usage personnel élémentaire",
    "A2": "Élémentaire — usage personnel",
    "B1": "Intermédiaire — usage social",
    "B2": "Avancé — usage professionnel opérationnel",
    "C1": "Professionnel — usage avancé et académique",
    "C2": "Expert — maîtrise quasi native",
}


def new_state(lang: str) -> dict:
    return dict(lang=lang, idx=2, asked=[], results=[], current=None, done=False)


def next_question(state: dict, bank: pd.DataFrame) -> dict | None:
    if len(state["asked"]) >= N_DIAG:
        state["done"] = True
        return None
    pool = bank[(bank.lang == state["lang"]) & (~bank.id.isin(state["asked"]))]
    if pool.empty:
        state["done"] = True
        return None
    used_skills = [r["skill"] for r in state["results"][-3:]]
    # cherche au niveau courant, puis aux niveaux voisins
    for delta in (0, 1, -1, 2, -2, 3, -3):
        i = state["idx"] + delta
        if 0 <= i < 6:
            cand = pool[pool.level == S.LEVELS[i]]
            fresh = cand[~cand.skill.isin(used_skills)]
            cand = fresh if not fresh.empty else cand
            if not cand.empty:
                q = cand.sample(1, random_state=random.randint(0, 10**6)).iloc[0].to_dict()
                opts = q["options"].split("|")
                random.shuffle(opts)
                q["shuffled"] = opts
                state["current"] = q
                return q
    state["done"] = True
    return None


def answer(state: dict, choice: str, seconds: float) -> bool:
    q = state["current"]
    ok = choice == q["answer"]
    state["asked"].append(q["id"])
    state["results"].append(dict(id=q["id"], level=q["level"], skill=q["skill"], correct=int(ok),
                                 seconds=round(seconds, 1), explanation=q["explanation"],
                                 question=q["question"], answer=q["answer"], choice=choice))
    state["idx"] = min(5, state["idx"] + 1) if ok else max(0, state["idx"] - 1)
    state["current"] = None
    if len(state["asked"]) >= N_DIAG:
        state["done"] = True
    return ok


def features(results: list[dict]) -> dict:
    df = pd.DataFrame(results)
    f = {}
    overall = df.correct.mean() if not df.empty else 0
    for s in S.SKILLS:
        d = df[df.skill == s]
        f[f"acc_{s}"] = float(d.correct.mean()) if not d.empty else float(overall)
    f["mean_seconds"] = float(df.seconds.mean()) if not df.empty else 20
    passed = [S.LEVELS.index(l) for l, g in df.groupby("level") if g.correct.mean() >= .5]
    f["max_level_passed"] = max(passed) if passed else -1
    f["accuracy"] = float(overall)
    return f


def rule_level(results: list[dict]) -> str:
    """Plus haut niveau réussi à ≥ 50 % sans échec complet aux niveaux inférieurs."""
    df = pd.DataFrame(results)
    best = 0
    for i, l in enumerate(S.LEVELS):
        g = df[df.level == l]
        if g.empty:
            continue
        enough = len(g) >= 2 or i <= 2          # C1/C2 : au moins 2 items réussis à ce niveau
        if g.correct.mean() >= .5 and enough and g.correct.sum() >= (2 if i >= 4 else 1):
            best = i
        elif i <= best:
            best = max(0, i - 1)
    return S.LEVELS[best]


def finalize(state: dict, models: dict) -> dict:
    res = state["results"]
    f = features(res)
    rule = rule_level(res)
    ml_lvl, conf, proba = ML.predict_level(models, f)
    # fusion : moyenne pondérée des indices de niveau (ML pondéré par sa confiance)
    fused = round((S.LEVELS.index(rule) * (1 - conf * .5) + S.LEVELS.index(ml_lvl) * conf * .5)
                  / ((1 - conf * .5) + conf * .5))
    level = S.LEVELS[int(np.clip(fused, 0, 5))]
    df = pd.DataFrame(res)
    per_skill = {s: (round(df[df.skill == s].correct.mean() * 100) if (df.skill == s).any() else None)
                 for s in S.SKILLS}
    return dict(level=level, rule_level=rule, ml_level=ml_lvl, ml_confidence=round(conf, 2), proba=proba,
                score=round(f["accuracy"] * 100), per_skill=per_skill, usage=USAGE[level], results=res)


# ---------------------------------------------------------------- évaluation certifiante
def build_exam(bank: pd.DataFrame, lang: str, level: str) -> list[dict]:
    i = S.LEVELS.index(level)
    pool = bank[bank.lang == lang]
    target = pool[pool.level == level]
    below = pool[pool.level == S.LEVELS[max(0, i - 1)]] if i > 0 else pool.iloc[0:0]
    above = pool[pool.level == S.LEVELS[min(5, i + 1)]] if i < 5 else pool.iloc[0:0]
    exam = pd.concat([target, below, above.sample(min(2, len(above)), random_state=1)])
    items = []
    for _, r in exam.sample(frac=1, random_state=random.randint(0, 999)).iterrows():
        q = r.to_dict()
        opts = q["options"].split("|")
        random.shuffle(opts)
        q["shuffled"] = opts
        items.append(q)
    return items


def grade_exam(items: list[dict], answers: dict, level: str) -> dict:
    tot = len(items)
    good = sum(1 for q in items if answers.get(q["id"]) == q["answer"])
    tgt = [q for q in items if q["level"] == level]
    tgt_good = sum(1 for q in tgt if answers.get(q["id"]) == q["answer"])
    score = round(100 * good / tot) if tot else 0
    tgt_score = round(100 * tgt_good / len(tgt)) if tgt else score
    per_skill = {}
    for s in S.SKILLS:
        qs = [q for q in items if q["skill"] == s]
        if qs:
            per_skill[s] = round(100 * sum(answers.get(q["id"]) == q["answer"] for q in qs) / len(qs))
    passed = score >= 70 and tgt_score >= 60
    if score >= 90:
        mention = "Excellence"
    elif score >= 80:
        mention = "Très bien"
    elif score >= 70:
        mention = "Bien"
    else:
        mention = "—"
    return dict(score=score, target_score=tgt_score, passed=passed, per_skill=per_skill, mention=mention)
