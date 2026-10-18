"""
Moteur de Machine Learning de LinguaPilot.

1. Classifieur de niveau CECRL (RandomForest) — affine le diagnostic adaptatif.
2. Traçage des connaissances (régression logistique) — probabilité de réussir un item,
   utilisée pour choisir des exercices dans la « zone proximale » (~70 % de réussite).
3. Profils d'apprenants (KMeans) — segmente les forces / faiblesses.
4. Prévision de progression (régression linéaire) sur l'historique de l'utilisateur.

Les modèles démarrent sur des données synthétiques (data/ml/*.csv, générées ici)
puis sont réentraînés en ajoutant les données réelles des utilisateurs (attempts.csv,
diagnostics.csv) dès qu'elles existent.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from . import storage as S

SK = list(S.SKILLS)
FEATURES = [f"acc_{s}" for s in SK] + ["mean_seconds", "max_level_passed", "accuracy"]
RNG = np.random.default_rng(42)


# ---------------------------------------------------------------- données synthétiques
def generate_synthetic(n_learners: int = 3000, n_attempts: int = 40000) -> None:
    """Crée data/ml/synthetic_learners.csv et data/ml/synthetic_attempts.csv."""
    rows = []
    for _ in range(n_learners):
        t = RNG.integers(0, 6)                       # vrai niveau 0..5
        bias = RNG.normal(0, 0.9, len(SK))           # profil : forces/faiblesses
        accs = []
        for j in range(len(SK)):
            ability = t + bias[j]
            # réussite moyenne sur des items de niveau 0..5
            p = np.mean([1 / (1 + np.exp(-(ability - d + 0.3) * 1.4)) for d in range(6)])
            accs.append(np.clip(p + RNG.normal(0, 0.12), 0, 1))
        passed = [d for d in range(6) if 1 / (1 + np.exp(-(t - d + 0.3) * 1.4)) + RNG.normal(0, .25) >= .5]
        rows.append(dict(**{f"acc_{s}": round(a, 3) for s, a in zip(SK, accs)},
                         mean_seconds=round(max(4, RNG.normal(25 - 2.5 * t, 5)), 1),
                         max_level_passed=max(passed) if passed else -1,
                         accuracy=round(float(np.mean(accs)), 3),
                         level=S.LEVELS[t]))
    pd.DataFrame(rows).to_csv(S.MLDATA / "synthetic_learners.csv", index=False)

    att = []
    for _ in range(n_attempts):
        mastery = RNG.uniform(0, 1)
        gap = RNG.integers(-3, 4)
        n = RNG.integers(0, 40)
        logit = 3.2 * (mastery - .5) - .9 * gap + .25 * np.log1p(n)
        correct = int(RNG.uniform() < 1 / (1 + np.exp(-logit)))
        att.append(dict(mastery=round(mastery, 3), level_gap=gap, n_prior=n, correct=correct))
    pd.DataFrame(att).to_csv(S.MLDATA / "synthetic_attempts.csv", index=False)


def _ensure_synthetic():
    if not (S.MLDATA / "synthetic_learners.csv").exists() or not (S.MLDATA / "synthetic_attempts.csv").exists():
        generate_synthetic()


# ---------------------------------------------------------------- entraînement
def train_models() -> dict:
    _ensure_synthetic()
    learners = pd.read_csv(S.MLDATA / "synthetic_learners.csv")

    # données réelles : diagnostics validés
    real = S.read("diagnostics")
    if not real.empty:
        r = pd.DataFrame({f"acc_{s}": pd.to_numeric(real[s], errors="coerce") / 100 for s in SK})
        r["mean_seconds"] = 20.0
        r["max_level_passed"] = real["level"].map({l: i for i, l in enumerate(S.LEVELS)})
        r["accuracy"] = pd.to_numeric(real["score"], errors="coerce") / 100
        r["level"] = real["level"]
        learners = pd.concat([learners, r.dropna()], ignore_index=True)

    X, y = learners[FEATURES], learners["level"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=0, stratify=y)
    rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=0, n_jobs=-1).fit(Xtr, ytr)
    rf_acc = accuracy_score(yte, rf.predict(Xte))

    att = pd.read_csv(S.MLDATA / "synthetic_attempts.csv")
    A = att[["mastery", "level_gap", "n_prior"]].assign(n_prior=lambda d: np.log1p(d.n_prior))
    Atr, Ate, btr, bte = train_test_split(A, att["correct"], test_size=.2, random_state=0)
    kt = LogisticRegression().fit(Atr, btr)
    kt_auc = roc_auc_score(bte, kt.predict_proba(Ate)[:, 1])

    km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(learners[[f"acc_{s}" for s in SK]]
                                                            .sub(learners["accuracy"], axis=0))
    metrics = dict(rf_accuracy=round(rf_acc, 3), kt_auc=round(kt_auc, 3),
                   n_learners=len(learners), n_attempts=len(att), n_real_diag=len(real))
    pd.DataFrame([dict(ts=S.now(), **metrics)]).to_csv(S.MLDATA / "model_metrics.csv", index=False)
    return dict(rf=rf, kt=kt, km=km, metrics=metrics,
                importances=dict(zip(FEATURES, rf.feature_importances_.round(3))))


# ---------------------------------------------------------------- inférence
def predict_level(models: dict, feats: dict) -> tuple[str, float, dict]:
    x = pd.DataFrame([[feats.get(f, 0) for f in FEATURES]], columns=FEATURES)
    proba = models["rf"].predict_proba(x)[0]
    classes = models["rf"].classes_
    i = int(np.argmax(proba))
    return classes[i], float(proba[i]), dict(zip(classes, proba.round(3)))


def p_correct(models: dict, mastery: float, level_gap: int, n_prior: int) -> float:
    x = pd.DataFrame([[mastery, level_gap, np.log1p(n_prior)]], columns=["mastery", "level_gap", "n_prior"])
    return float(models["kt"].predict_proba(x)[0, 1])


PROFILE_NAMES = {
    "grammaire": "🧱 Architecte de la phrase", "vocabulaire": "📚 Collectionneur de mots",
    "comprehension": "🎧 Oreille fine", "registre": "🎩 Caméléon des registres",
    "culture": "🎭 Explorateur culturel",
}


def learner_profile(mastery: dict) -> tuple[str, str, str]:
    """Retourne (nom de profil, compétence forte, compétence à travailler)."""
    if not mastery:
        return "🌱 Nouvel explorateur", "-", "-"
    strong = max(mastery, key=mastery.get)
    weak = min(mastery, key=mastery.get)
    return PROFILE_NAMES[strong], strong, weak


def skill_mastery(attempts: pd.DataFrame, half_life_days: float = 14) -> dict:
    """Maîtrise par compétence : moyenne bayésienne lissée, pondérée par la récence."""
    out = {}
    if attempts.empty:
        return out
    df = attempts.copy()
    df["correct"] = pd.to_numeric(df["correct"], errors="coerce").fillna(0)
    age = (pd.Timestamp.now() - pd.to_datetime(df["ts"], errors="coerce")).dt.total_seconds() / 86400
    df["w"] = 0.5 ** (age.fillna(0) / half_life_days)
    for s in SK:
        d = df[df["skill"] == s]
        if d.empty:
            continue
        out[s] = round(float((1 + (d.correct * d.w).sum()) / (2 + d.w.sum())), 3)  # prior Beta(1,1)
    return out


def recommend_questions(models: dict, questions: pd.DataFrame, attempts: pd.DataFrame,
                        level: str, n: int = 8, skill: str | None = None, target_p: float = .7) -> pd.DataFrame:
    """Sélectionne les items les plus formateurs : p(réussite) proche de 70 %,
    bonus pour les compétences faibles et les items ratés à revoir (répétition espacée)."""
    if questions.empty:
        return questions
    mast = skill_mastery(attempts)
    lvl = S.LEVELS.index(level) if level in S.LEVELS else 2
    q = questions.copy()
    if skill:
        q = q[q.skill == skill]
    counts = attempts.groupby("question_id").size() if not attempts.empty else pd.Series(dtype=int)
    wrong = set(attempts[attempts.correct.astype(str) == "0"].question_id) if not attempts.empty else set()
    right = set(attempts[attempts.correct.astype(str) == "1"].question_id) if not attempts.empty else set()
    scores = []
    for _, r in q.iterrows():
        m = mast.get(r.skill, .5)
        gap = S.LEVELS.index(r.level) - lvl
        p = p_correct(models, m, gap, int(counts.get(r.id, 0)))
        s = -abs(p - target_p) + (1 - m) * .3 + (.4 if r.id in wrong else 0) - (.35 if r.id in right else 0)
        scores.append((s + RNG.normal(0, .03), p))
    q["priority"] = [s for s, _ in scores]
    q["p_success"] = [round(p, 2) for _, p in scores]
    return q.sort_values("priority", ascending=False).head(n)


def forecast_progress(diags: pd.DataFrame) -> dict | None:
    """Régression linéaire du score de diagnostic dans le temps → jours avant le prochain palier."""
    if len(diags) < 2:
        return None
    d = diags.copy()
    d["t"] = (pd.to_datetime(d.ts) - pd.to_datetime(d.ts).min()).dt.total_seconds() / 86400
    d["score"] = pd.to_numeric(d.score, errors="coerce")
    lr = LinearRegression().fit(d[["t"]], d["score"])
    slope = float(lr.coef_[0])
    last = float(d.score.iloc[-1])
    nxt = (int(last // 15) + 1) * 15
    days = (nxt - last) / slope if slope > 0.01 else None
    return dict(slope_per_week=round(slope * 7, 2), next_threshold=nxt,
                days_to_next=round(days) if days else None)
