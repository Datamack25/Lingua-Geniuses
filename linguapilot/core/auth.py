"""Comptes utilisateurs : création, connexion (PBKDF2-SHA256 salé, 200 000 itérations)."""
from __future__ import annotations
import hashlib, hmac, os, re, uuid
from . import storage as S

ITER = 200_000


def _hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITER).hex()


def register(username: str, email: str, display_name: str, password: str,
             native_lang: str = "fr", goal: str = "") -> tuple[bool, str]:
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_.-]{3,30}", username):
        return False, "Identifiant : 3 à 30 caractères (lettres, chiffres, . _ -)."
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères."
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
        return False, "Adresse e-mail invalide."
    users = S.read("users")
    if (users["username"] == username).any():
        return False, "Cet identifiant est déjà utilisé."
    salt = os.urandom(16).hex()
    uid = uuid.uuid4().hex[:12]
    S.append("users", dict(user_id=uid, username=username, email=email.strip(),
                           display_name=display_name.strip() or username, pwd_hash=_hash(password, salt),
                           salt=salt, native_lang=native_lang, goal=goal, created_at=S.now(), last_login=S.now()))
    S.append("notifications", dict(ts=S.now(), user_id=uid, kind="bienvenue",
             title="Bienvenue sur LinguaPilot 🎉",
             body="Commencez par le diagnostic d'Atlas : 10 minutes pour connaître votre niveau réel.",
             read="0"))
    return True, uid


def login(username: str, password: str) -> dict | None:
    users = S.read("users")
    row = users[users["username"] == username.strip().lower()]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    if not hmac.compare_digest(_hash(password, r["salt"]), r["pwd_hash"]):
        return None
    users.loc[row.index, "last_login"] = S.now()
    S.write("users", users)
    return r


def get_user(user_id: str) -> dict | None:
    users = S.read("users")
    row = users[users["user_id"] == user_id]
    return None if row.empty else row.iloc[0].to_dict()
