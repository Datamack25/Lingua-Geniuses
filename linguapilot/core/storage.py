"""Couche de données : contenus pédagogiques (lecture) + données utilisateurs (CSV)."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import threading
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "data" / "content"
USERDATA = ROOT / "data" / "user_data"
MLDATA = ROOT / "data" / "ml"
for p in (USERDATA, MLDATA):
    p.mkdir(parents=True, exist_ok=True)

LANGS = {"en": "🇬🇧 Anglais", "fr": "🇫🇷 Français", "es": "🇪🇸 Espagnol", "ht": "🇭🇹 Créole haïtien"}
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SKILLS = {
    "grammaire": "Grammaire",
    "vocabulaire": "Vocabulaire",
    "comprehension": "Compréhension",
    "registre": "Registres",
    "culture": "Culture",
}

# Schéma des tables utilisateurs (créées vides au premier lancement)
SCHEMAS = {
    "users": ["user_id", "username", "email", "display_name", "pwd_hash", "salt", "native_lang",
              "goal", "created_at", "last_login"],
    "attempts": ["ts", "user_id", "lang", "question_id", "level", "skill", "correct", "seconds", "context"],
    "diagnostics": ["ts", "user_id", "lang", "level", "score", "ml_level", "ml_confidence",
                    "grammaire", "vocabulaire", "comprehension", "registre", "culture", "usage"],
    "writings": ["ts", "user_id", "lang", "register_target", "words", "level_est", "etendue",
                 "correction", "coherence", "adequation", "global", "register_detected"],
    "certificates": ["cert_id", "ts", "user_id", "display_name", "lang", "level", "score", "usage", "hash"],
    "notifications": ["ts", "user_id", "kind", "title", "body", "read"],
    "xp_log": ["ts", "user_id", "xp", "reason", "lang"],
}

_lock = threading.Lock()


def _path(table: str) -> Path:
    return USERDATA / f"{table}.csv"


def read(table: str) -> pd.DataFrame:
    p = _path(table)
    if not p.exists():
        pd.DataFrame(columns=SCHEMAS[table]).to_csv(p, index=False)
    try:
        return pd.read_csv(p, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=SCHEMAS[table])


def append(table: str, row: dict) -> None:
    with _lock:
        df = read(table)
        row = {k: row.get(k, "") for k in SCHEMAS[table]}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(_path(table), index=False)


def append_many(table: str, rows: list[dict]) -> None:
    if not rows:
        return
    with _lock:
        df = read(table)
        new = pd.DataFrame([{k: r.get(k, "") for k in SCHEMAS[table]} for r in rows])
        pd.concat([df, new], ignore_index=True).to_csv(_path(table), index=False)


def write(table: str, df: pd.DataFrame) -> None:
    with _lock:
        df.to_csv(_path(table), index=False)


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def content(name: str) -> pd.DataFrame:
    return pd.read_csv(CONTENT / f"{name}.csv", keep_default_na=False)


def user_rows(table: str, user_id: str, lang: str | None = None) -> pd.DataFrame:
    df = read(table)
    df = df[df["user_id"] == user_id]
    if lang and "lang" in df.columns:
        df = df[df["lang"] == lang]
    return df
